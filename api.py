"""
DeepFind Agent - FastAPI 后端接口

提供 REST API 和 SSE 流式输出支持
"""

import asyncio
import json
import os
import sys
import uuid
import time
import threading
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, List, Dict, Any, Set
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from utils import generate_html, generate_markdown_file
from agents import (
    run_search, run_analyze, run_report, run_enhanced_report, run_extraction, run_validation,
    plan_tasks_for_query, visualize_dag, get_task_summary, TaskExecutor, create_task_handlers
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from schemas.tasks import TaskPlan

# 导入新的业务调研 prompt
from prompts.business_research_prompts import (
    BUSINESS_RESEARCH_SYSTEM_PROMPT,
    BUSINESS_CLASSIFICATION_PROMPT,
    COMPETITIVE_ANALYSIS_PROMPT,
    GUIDE_GENERATION_PROMPT,
    PRODUCT_ANALYSIS_PROMPT,
)

# 导入新的Few-shot示例驱动的Prompt
from prompts.guide_prompts_v2 import (
    GUIDE_GENERATION_PROMPT_V2,
    GUIDE_FROM_ENTITIES_PROMPT,
    select_few_shot_example,
    format_entities_for_prompt,
)

# 导入报告生成辅助函数
# report_agent functions are now called through run_report

# 使用业务调研 prompt 替代原有的通用 prompt
ENHANCED_REPORT_SYSTEM_PROMPT = BUSINESS_RESEARCH_SYSTEM_PROMPT


def classify_query_simple(query: str) -> str:
    """
    简化版查询分类 - 仅用于任务计划和进度展示

    所有查询都走相同的处理流程，输出格式由内容类型自动决定

    返回值：
    - 'standard': 标准处理流程（搜索→分析→提取→生成）
    """
    # 所有查询统一处理，返回标准流程
    return 'standard'


# 保留旧函数名兼容
def classify_query_complexity(query: str) -> str:
    """兼容旧接口"""
    return classify_query_simple(query)


# 简单问题直接回答的系统 prompt
SIMPLE_QA_PROMPT = """你是一个智能助手，请根据搜索结果直接、简洁地回答用户问题。

## 回答原则

1. **直接回答**：不要写报告，直接给出答案
2. **简洁明了**：用最少的文字说清楚
3. **引用来源**：重要信息标注来源 [编号]
4. **结构化**：如果信息较多，用表格或列表组织
5. **不要废话**：不要说"根据搜索结果"、"经过分析"等套话

## 输出格式

根据问题类型选择合适格式：

### 价格/数值类
直接给出数字，可加简短说明
```
约 ¥XX-XX 元

- 来源XX显示：XX元
- 来源YY显示：XX元
```

### 是非类
先给结论，再简述原因
```
是的/不是/可以/不可以

原因：...
```

### 列表类
用表格或列表
```
| 项目 | 信息 |
|------|------|
| A | xxx |
| B | xxx |
```

### 定义类
一句话定义 + 简要说明
```
XX是...（一句话定义）

简要说明：...
```

请直接回答，不要写报告格式。"""


# 快速回答函数
async def generate_quick_answer(query: str, search_results: list, model: str) -> str:
    """对简单问题生成快速回答"""
    from langchain_deepseek import ChatDeepSeek

    llm = ChatDeepSeek(
        model=model or settings.deepseek_model,
        temperature=0.3,
        api_key=settings.deepseek_api_key,
    )

    # 准备简洁的上下文
    context = "搜索结果：\n\n"
    for i, item in enumerate(search_results[:5], 1):
        title = item.get('title', '')
        content = item.get('content', item.get('snippet', ''))[:500]
        context += f"[{i}] {title}\n{content}\n\n"

    context += f"\n问题：{query}\n\n请根据以上信息直接回答问题，不要写成报告格式。"

    messages = [
        SystemMessage(content=SIMPLE_QA_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    return response.content

# 会话存储 - 使用线程安全的锁
_session_lock = threading.Lock()
research_sessions: Dict[str, Dict[str, Any]] = {}
cancelled_sessions: Set[str] = set()
MAX_SESSIONS = 100
SESSION_TTL_SECONDS = 3600  # 会话存活时间：1小时


def generate_session_id() -> str:
    """生成安全的会话ID - 使用完整UUID"""
    return str(uuid.uuid4())


def cleanup_sessions():
    """清理过期会话，防止内存泄漏"""
    global research_sessions, cancelled_sessions

    with _session_lock:
        current_time = time.time()

        # 清理过期会话
        expired = [
            sid for sid, data in research_sessions.items()
            if current_time - data.get('timestamp', 0) > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            research_sessions.pop(sid, None)
            cancelled_sessions.discard(sid)

        # 如果仍然超过限制，保留最新的
        if len(research_sessions) > MAX_SESSIONS:
            sorted_sessions = sorted(
                research_sessions.items(),
                key=lambda x: x[1].get('timestamp', 0),
                reverse=True
            )
            research_sessions = dict(sorted_sessions[:MAX_SESSIONS])

        # 同步取消集合
        cancelled_sessions = cancelled_sessions & set(research_sessions.keys())


class ResearchDepth(str, Enum):
    """调研深度枚举"""
    SHALLOW = "shallow"
    DEEP = "deep"


class ResearchRequest(BaseModel):
    """调研请求"""
    query: str
    depth: ResearchDepth = ResearchDepth.DEEP

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('查询内容不能为空')
        if len(v) > 2000:
            raise ValueError('查询内容不能超过2000个字符')
        return v.strip()


class ResearchStatus(BaseModel):
    """调研状态"""
    session_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    current_step: str
    message: str
    search_count: int = 0
    analyzed_count: int = 0
    report: Optional[str] = None
    sources: List[Dict] = []
    output_files: Dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 DeepFind Agent API 启动中...")
    yield
    logger.info("👋 DeepFind Agent API 关闭中...")


app = FastAPI(
    title="DeepFind Agent API",
    description="深度调研 Agent 后端接口",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置 - 从环境变量读取允许的来源
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://deepfind-agent.vercel.app").split(",")
# 开发模式下允许所有来源，生产环境应配置具体域名
CORS_ORIGINS = ["*"] if os.getenv("ENV", "development") == "development" else ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_api_keys():
    """检查 API 配置"""
    issues = []
    if not settings.deepseek_api_key:
        issues.append("DeepSeek API Key 未配置")
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        issues.append("Tavily API Key 未配置")
    return issues


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "DeepFind Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    issues = check_api_keys()
    return {
        "status": "healthy" if not issues else "degraded",
        "issues": issues,
        "config": {
            "deepseek_configured": bool(settings.deepseek_api_key),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY", "")),
            "search_depth": settings.search_depth,
        }
    }


@app.get("/api/plan")
async def get_task_plan(query: str):
    """
    获取任务计划（不执行）

    返回任务的DAG结构、并行层级和预估时间
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")

    query = query.strip()
    query_type = classify_query_complexity(query)

    # 创建任务计划
    plan = plan_tasks_for_query(query, query_type)
    summary = get_task_summary(plan)
    dag_visual = visualize_dag(plan)

    return {
        "plan_id": plan.plan_id,
        "query": query,
        "query_type": query_type,
        "tasks": [
            {
                "id": t.id,
                "name": t.name,
                "type": t.task_type,
                "description": t.description,
                "dependencies": t.dependencies,
                "priority": t.priority,
                "status": t.status,
            }
            for t in plan.tasks
        ],
        "execution_order": plan.execution_order,
        "parallel_groups": plan.parallel_groups,
        "dag_visualization": dag_visual,
        "summary": summary,
    }


@app.post("/api/research")
async def start_research(request: ResearchRequest):
    """
    启动调研任务（同步模式）

    返回 session_id，客户端可轮询状态
    """
    import uuid

    session_id = str(uuid.uuid4())[:8]

    # 初始化状态
    research_sessions[session_id] = {
        "status": "pending",
        "progress": 0,
        "current_step": "初始化",
        "message": "正在启动调研...",
        "query": request.query,
        "search_count": 0,
        "analyzed_count": 0,
        "report": None,
        "sources": [],
        "output_files": {},
        "errors": [],
        "todos": [],
        "timestamp": datetime.now().timestamp(),
    }

    # 清理旧会话
    cleanup_sessions()

    return {
        "session_id": session_id,
        "status": "pending",
        "message": "调研任务已创建，请使用 SSE 获取实时进度"
    }


@app.get("/api/research/{session_id}/status")
async def get_research_status(session_id: str):
    """获取调研状态"""
    with _session_lock:
        if session_id not in research_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return research_sessions[session_id].copy()


@app.post("/api/research/{session_id}/cancel")
async def cancel_research(session_id: str):
    """取消调研任务"""
    with _session_lock:
        cancelled_sessions.add(session_id)
        if session_id in research_sessions:
            research_sessions[session_id]["status"] = "cancelled"
    return {"status": "cancelled", "session_id": session_id}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话记录"""
    with _session_lock:
        # 从会话存储中删除
        if session_id in research_sessions:
            del research_sessions[session_id]
            # 从取消集合中移除
            cancelled_sessions.discard(session_id)
            return {"status": "deleted", "session_id": session_id}
        else:
            # 即使不存在也返回成功，确保幂等性
            cancelled_sessions.discard(session_id)
            return {"status": "not_found", "session_id": session_id}


@app.get("/api/download")
async def download_file(path: str, format: str = "markdown"):
    """
    下载生成的报告文件

    Args:
        path: 文件绝对路径
        format: 文件格式 (markdown/html)
    """
    from fastapi.responses import FileResponse
    import mimetypes

    # 安全检查：确保文件路径在 outputs 目录内
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    abs_path = os.path.abspath(path)

    if not abs_path.startswith(os.path.abspath(outputs_dir)):
        raise HTTPException(status_code=403, detail="禁止访问此路径")

    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 获取文件名
    filename = os.path.basename(abs_path)

    # 根据格式设置 MIME 类型
    if format == "markdown" or abs_path.endswith(".md"):
        media_type = "text/markdown"
    elif format == "html" or abs_path.endswith(".html"):
        media_type = "text/html"
    else:
        media_type = mimetypes.guess_type(abs_path)[0] or "application/octet-stream"

    return FileResponse(
        path=abs_path,
        filename=filename,
        media_type=media_type
    )


@app.get("/api/research/stream")
async def research_stream(query: str, depth: str = "deep", model: str = "deepseek-reasoner"):
    """
    调研流式接口（SSE）

    实时返回调研进度和结果

    Args:
        query: 调研查询（必填，最大2000字符）
        depth: 搜索深度 (shallow/deep)
        model: 使用的模型 (deepseek-reasoner/deepseek-chat)
    """
    # 输入验证
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="查询内容不能超过2000个字符")

    session_id = generate_session_id()  # 使用安全的 Session ID 生成
    query = query.strip()
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # 确保该会话不在取消列表中
    with _session_lock:
        cancelled_sessions.discard(session_id)

    # 验证模型参数
    valid_models = ["deepseek-reasoner", "deepseek-chat"]
    if model not in valid_models:
        model = "deepseek-reasoner"

    async def event_generator() -> AsyncGenerator[str, None]:
        """SSE 事件生成器"""

        def send_event(event_type: str, data: Dict) -> str:
            """格式化 SSE 事件"""
            return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

        def is_cancelled() -> bool:
            """检查是否被取消"""
            return session_id in cancelled_sessions

        try:
            # Step 1: 任务规划
            if is_cancelled():
                yield send_event("cancelled", {"session_id": session_id, "message": "任务已取消"})
                return

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 5,
                "step": "任务规划",
                "message": "正在分析调研需求，规划执行步骤..."
            })

            # 判断问题复杂度
            query_complexity = classify_query_complexity(query)
            logger.info(f"[{session_id}] 问题复杂度: {query_complexity}")

            # 创建结构化任务计划
            task_plan = plan_tasks_for_query(query, query_complexity, model)

            # 生成任务列表和DAG可视化
            task_list = [{
                "id": t.id,
                "name": t.name,
                "type": t.task_type,
                "description": t.description,
                "dependencies": t.dependencies,
                "priority": t.priority,
                "status": t.status
            } for t in task_plan.tasks]

            dag_visual = visualize_dag(task_plan)
            summary = get_task_summary(task_plan)

            logger.info(f"[{session_id}] 任务计划创建完成: {len(task_plan.tasks)} 个任务, {len(task_plan.parallel_groups)} 个并行层级")

            yield send_event("task_plan", {
                "session_id": session_id,
                "plan_id": task_plan.plan_id,
                "query_type": query_complexity,
                "tasks": task_list,
                "parallel_groups": task_plan.parallel_groups,
                "dag": dag_visual,
                "summary": summary
            })

            # 兼容旧版本的todos事件
            todos = [t.name for t in task_plan.tasks]
            yield send_event("todos", {
                "session_id": session_id,
                "todos": todos
            })

            # Step 2: 并行执行搜索任务
            if is_cancelled():
                yield send_event("cancelled", {"session_id": session_id, "message": "任务已取消"})
                return

            # 获取第一层可并行的任务（无依赖的任务）
            search_tasks = [t for t in task_plan.tasks if t.task_type == "search"]
            parallel_search_count = len(search_tasks)

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 10,
                "step": "执行搜索",
                "message": f"正在并行执行 {parallel_search_count} 个搜索任务..."
            })

            # 定义单个搜索任务的执行函数（纯异步函数，不yield）
            async def execute_single_search(task):
                """执行单个搜索任务"""
                dimension_queries = task.input_data.get("queries", [query])
                dimension = task.input_data.get("dimension", "general")

                results = []
                for q in dimension_queries[:3]:
                    result = await asyncio.to_thread(run_search, q)
                    if result.get("search_results"):
                        for r in result["search_results"]:
                            r["dimension"] = dimension
                            r["search_query"] = q
                        results.extend(result["search_results"])

                return {"task_id": task.id, "task_name": task.name, "results": results, "dimension": dimension}

            # 并行执行所有搜索
            all_search_results = []

            if search_tasks:
                # 先发送所有任务开始状态
                for task in search_tasks:
                    yield send_event("task_status", {
                        "session_id": session_id,
                        "task_id": task.id,
                        "status": "running",
                        "message": f"执行: {task.name}"
                    })

                # 使用 asyncio.as_completed 获取完成顺序，实现实时状态更新
                search_coroutines = [execute_single_search(task) for task in search_tasks]
                for coro in asyncio.as_completed(search_coroutines):
                    try:
                        result = await coro
                        all_search_results.extend(result.get("results", []))
                        # 发送任务完成状态
                        yield send_event("task_status", {
                            "session_id": session_id,
                            "task_id": result["task_id"],
                            "status": "completed",
                            "message": f"完成: {result['task_name']} ({len(result['results'])}条结果)"
                        })
                    except Exception as e:
                        logger.error(f"搜索任务失败: {e}")
            else:
                # 降级：执行默认搜索
                yield send_event("tool_start", {
                    "session_id": session_id,
                    "tool": "search",
                    "input": query,
                    "message": "正在启动搜索..."
                })
                search_result = await asyncio.to_thread(run_search, query)
                all_search_results = search_result.get("search_results", [])

            # 去重
            seen_urls = set()
            search_results = []
            for r in all_search_results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    search_results.append(r)

            search_count = len(search_results)

            yield send_event("tool_end", {
                "session_id": session_id,
                "tool": "search",
                "output_summary": f"找到 {search_count} 条相关结果",
                "count": search_count
            })

            yield send_event("search", {
                "session_id": session_id,
                "count": search_count,
                "results": [
                    {"title": r.get("title", ""), "url": r.get("url", ""), "dimension": r.get("dimension", "general")}
                    for r in search_results[:15]
                ]
            })

            if not search_results:
                yield send_event("error", {
                    "session_id": session_id,
                    "message": "搜索无结果，请尝试其他关键词"
                })
                return

            # Step 3: 分析内容
            if is_cancelled():
                yield send_event("cancelled", {"session_id": session_id, "message": "任务已取消"})
                return

            # 更新分析任务状态
            analyze_tasks = [t for t in task_plan.tasks if t.task_type == "analyze"]
            for task in analyze_tasks:
                yield send_event("task_status", {
                    "session_id": session_id,
                    "task_id": task.id,
                    "status": "running",
                    "message": f"执行: {task.name}"
                })

            yield send_event("tool_start", {
                "session_id": session_id,
                "tool": "analyze",
                "input": f"解析 {min(search_count, 10)} 个网页",
                "message": "正在启动内容分析..."
            })

            # 显示将要访问的 URL
            for i, r in enumerate(search_results[:10]):
                yield send_event("page_progress", {
                    "session_id": session_id,
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "status": "pending",
                    "index": i + 1,
                    "total": min(search_count, 10)
                })

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 40,
                "step": "分析内容",
                "message": f"正在分析 {min(search_count, 10)} 个网页..."
            })

            # 使用 asyncio.to_thread 包装同步分析调用
            analyze_result = await asyncio.to_thread(run_analyze, search_results, model)
            analyzed_content = analyze_result.get("analyzed_content", [])
            key_findings = analyze_result.get("key_findings", "")

            # 显示解析成功的 URL
            for i, content in enumerate(analyzed_content):
                yield send_event("page_loaded", {
                    "session_id": session_id,
                    "url": content.get("url", ""),
                    "title": content.get("title", ""),
                    "status": "success",
                    "index": i + 1,
                    "total": len(analyzed_content)
                })

            yield send_event("tool_end", {
                "session_id": session_id,
                "tool": "analyze",
                "output_summary": f"成功分析 {len(analyzed_content)} 个网页",
                "count": len(analyzed_content)
            })

            yield send_event("analyze", {
                "session_id": session_id,
                "count": len(analyzed_content),
                "key_findings": key_findings[:500] + "..." if len(key_findings) > 500 else key_findings
            })

            # 标记分析任务完成
            for task in analyze_tasks:
                yield send_event("task_status", {
                    "session_id": session_id,
                    "task_id": task.id,
                    "status": "completed",
                    "message": f"完成: {task.name}"
                })

            if not analyzed_content:
                yield send_event("error", {
                    "session_id": session_id,
                    "message": "网页分析失败，请稍后重试"
                })
                return

            # Step 4: 智能提取与自适应报告生成（统一流程）
            if is_cancelled():
                yield send_event("cancelled", {"session_id": session_id, "message": "任务已取消"})
                return

            # 4.1 智能实体提取（所有查询统一执行）
            extract_tasks = [t for t in task_plan.tasks if t.task_type == "extract"]
            for task in extract_tasks:
                yield send_event("task_status", {
                    "session_id": session_id,
                    "task_id": task.id,
                    "status": "running",
                    "message": f"执行: {task.name}"
                })

            yield send_event("tool_start", {
                "session_id": session_id,
                "tool": "extraction",
                "input": "智能提取结构化信息",
                "message": "正在分析内容类型并提取信息..."
            })

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 55,
                "step": "智能提取",
                "message": "正在提取结构化信息..."
            })

            content_type = "unknown"
            entities = {}
            extraction_metadata = {}

            try:
                extraction_result = await asyncio.to_thread(
                    run_extraction, analyzed_content, query, model
                )
                entities = extraction_result.get("entities", {})
                content_type = extraction_result.get("content_type", "unknown")
                extraction_metadata = extraction_result.get("extraction_metadata", {})
                confidence_scores = extraction_result.get("confidence_scores", {})

                logger.info(f"[{session_id}] 智能提取完成，内容类型: {content_type}, 实体类型: {list(entities.keys())}")

                yield send_event("tool_end", {
                    "session_id": session_id,
                    "tool": "extraction",
                    "output_summary": f"识别为{content_type}类型，提取了 {sum(len(v) for v in entities.values() if isinstance(v, list))} 个实体",
                    "content_type": content_type,
                    "entities_count": {k: len(v) for k, v in entities.items() if isinstance(v, list)},
                    "confidence": confidence_scores
                })

                yield send_event("extraction", {
                    "session_id": session_id,
                    "content_type": content_type,
                    "entities": entities,
                    "confidence": confidence_scores
                })

                for task in extract_tasks:
                    yield send_event("task_status", {
                        "session_id": session_id,
                        "task_id": task.id,
                        "status": "completed",
                        "message": f"完成: {task.name}"
                    })

            except Exception as e:
                logger.error(f"[{session_id}] 智能提取失败: {str(e)}")
                entities = {}
                for task in extract_tasks:
                    yield send_event("task_status", {
                        "session_id": session_id,
                        "task_id": task.id,
                        "status": "failed",
                        "message": f"失败: {task.name} - {str(e)}"
                    })

            # 4.2 自适应报告生成
            report_tasks = [t for t in task_plan.tasks if t.task_type == "report"]
            for task in report_tasks:
                yield send_event("task_status", {
                    "session_id": session_id,
                    "task_id": task.id,
                    "status": "running",
                    "message": f"执行: {task.name}"
                })

            # 根据内容类型选择报告生成方式
            type_labels = {
                "weather": "天气信息",
                "product": "产品评测",
                "travel": "旅行攻略",
                "tech": "技术指南",
                "news": "新闻资讯",
                "qa": "问答",
                "other": "综合信息"
            }
            type_label = type_labels.get(content_type, "综合信息")

            yield send_event("tool_start", {
                "session_id": session_id,
                "tool": "report",
                "input": f"基于 {len(analyzed_content)} 个来源生成{type_label}",
                "message": "正在生成内容..."
            })

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 70,
                "step": "生成内容",
                "message": f"正在生成{type_label}..."
            })

            logger.info(f"[{session_id}] 开始自适应报告生成，内容类型: {content_type}")

            try:
                llm = ChatDeepSeek(
                    model=model,
                    temperature=0.7,
                    api_key=settings.deepseek_api_key,
                    streaming=True,
                )

                # 准备上下文（包含URL供LLM生成可点击链接）
                sources_context = ""
                for i, item in enumerate(analyzed_content[:10], 1):
                    title = item.get('title', '未知标题')
                    url = item.get('url', '')
                    content = item.get('content', '')[:1000]
                    sources_context += f"[来源 {i}] {title}\nURL: {url}\n{content}\n\n"

                # 准备实体信息
                entities_str = json.dumps(entities, ensure_ascii=False, indent=2) if entities else "{}"

                # 使用自适应报告 Prompt
                from prompts.adaptive_prompts import ADAPTIVE_REPORT_PROMPT
                report_prompt = ADAPTIVE_REPORT_PROMPT.format(
                    query=query,
                    entities=entities_str,
                    sources=sources_context[:8000]  # 限制长度
                )

                messages = [
                    SystemMessage(content=report_prompt),
                    HumanMessage(content="请根据提取的信息生成清晰、实用的报告，选择最适合内容的输出格式。")
                ]

                # 流式生成
                report_content = ""
                chunk_count = 0
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        chunk_count += 1
                        report_content += chunk.content
                        if chunk_count == 1:
                            logger.info(f"[{session_id}] 收到第一个报告 chunk")
                        yield send_event("llm_chunk", {
                            "session_id": session_id,
                            "content": chunk.content,
                            "is_thinking": False
                        })

                logger.info(f"[{session_id}] 报告生成完成，长度: {len(report_content)}")

                # 构建完整报告
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                entity_info = ""
                if entities:
                    entity_counts = {k: len(v) for k, v in entities.items() if isinstance(v, list)}
                    if entity_counts:
                        entity_info = f"\n**提取的信息类型**: {', '.join(f'{k}({v}个)' for k, v in entity_counts.items())}\n"

                # 构建来源列表
                sources = [
                    {"id": i + 1, "title": item.get("title", "未知标题"), "url": item.get("url", "")}
                    for i, item in enumerate(analyzed_content)
                ]

                # 生成参考资料章节（确保格式正确）
                references_section = "\n## 参考资料\n\n"
                for source in sources:
                    title = source.get("title", "未知标题")
                    url = source.get("url", "")
                    if url:
                        references_section += f"{source['id']}. [{title}]({url})\n"
                    else:
                        references_section += f"{source['id']}. {title}\n"

                report = f"""# {query}

**内容类型**：{type_label}
**生成时间**：{timestamp}
**数据来源**：{len(analyzed_content)} 个来源{entity_info}
---

{report_content}
{references_section}
---

*本报告由 DeepFind Agent 自动生成，信息来源于公开网络，仅供参考。*
"""

            except Exception as e:
                logger.error(f"[{session_id}] 报告生成失败: {str(e)}")
                report = f"# {query}\n\n抱歉，生成报告时出错：{str(e)}"
                sources = []

            yield send_event("tool_end", {
                "session_id": session_id,
                "tool": "report",
                "output_summary": f"报告生成完成，共 {len(report)} 字"
            })

            # 标记报告任务完成
            for task in report_tasks:
                yield send_event("task_status", {
                    "session_id": session_id,
                    "task_id": task.id,
                    "status": "completed",
                    "message": f"完成: {task.name}"
                })

            # Step 5: 生成输出文件
            if is_cancelled():
                yield send_event("cancelled", {"session_id": session_id, "message": "任务已取消"})
                return

            yield send_event("progress", {
                "session_id": session_id,
                "progress": 90,
                "step": "生成文件",
                "message": "正在生成报告文件..."
            })

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in query[:20] if c.isalnum() or c in " -_").strip()
            safe_query = safe_query.replace(" ", "_")

            output_files = {}

            # Markdown
            md_path = os.path.join(output_dir, f"report_{timestamp}_{safe_query}.md")
            md_success = await asyncio.to_thread(generate_markdown_file, report, md_path)
            if md_success:
                output_files["markdown"] = md_path

            # HTML
            html_path = os.path.join(output_dir, f"report_{timestamp}_{safe_query}.html")
            html_success = await asyncio.to_thread(generate_html, report, html_path, query)
            if html_success:
                output_files["html"] = html_path

            # 完成
            yield send_event("complete", {
                "session_id": session_id,
                "progress": 100,
                "report": report,
                "sources": sources,
                "output_files": output_files,
                "message": "调研完成！"
            })

        except Exception as e:
            yield send_event("error", {
                "session_id": session_id,
                "message": str(e)
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)