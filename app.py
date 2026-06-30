"""
DeepFind Agent - Streamlit 主界面

基于原型图设计的深度调研界面
"""

import os
import sys
import logging
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from workflow import run_deepfind_workflow

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="DeepFind Agent - 深度调研助手",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 自定义样式
st.markdown("""
<style>
    /* 隐藏默认的header和footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主容器样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* 标题样式 */
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }

    .sub-title {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* 输入框样式 */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-size: 1rem;
        min-height: 180px;
    }

    .stTextArea textarea:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
    }

    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        height: 48px;
        font-size: 1.1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        border: none;
        border-radius: 8px;
        color: white;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }

    .stButton > button:disabled {
        background: #ccc;
        transform: none;
        box-shadow: none;
    }

    /* 配置项样式 */
    .config-section {
        margin-top: 1.5rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }

    .config-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.8rem;
    }

    /* Radio按钮样式 */
    .stRadio > label {
        font-size: 0.85rem;
        color: #666;
    }

    .stRadio > div {
        flex-direction: row;
        gap: 1rem;
    }

    /* 右侧报告区域 */
    .report-content {
        font-size: 1rem;
        line-height: 1.8;
        color: #333;
    }

    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        color: #999;
        text-align: center;
    }

    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    /* 下载按钮区域 */
    .download-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e0;
    }

    /* 侧边栏隐藏 */
    section[data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "report" not in st.session_state:
        st.session_state.report = ""
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "todos" not in st.session_state:
        st.session_state.todos = []
    if "is_running" not in st.session_state:
        st.session_state.is_running = False
    if "output_files" not in st.session_state:
        st.session_state.output_files = {}
    if "errors" not in st.session_state:
        st.session_state.errors = []


def render_header():
    """渲染左侧标题"""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="main-title">🔍 DeepFind Agent</div>
        <div class="sub-title">AI 驱动的深度调研助手，一键生成专业调研报告</div>
    </div>
    """, unsafe_allow_html=True)


def render_input_area():
    """渲染输入区域"""
    query = st.text_area(
        "请输入您要调研的主题或问题",
        height=180,
        placeholder="例如：2024年中国新能源汽车市场格局分析\n\n或：微服务架构 vs 单体架构如何选择",
        key="query_input",
        label_visibility="collapsed",
    )
    return query


def render_config_options():
    """渲染配置选项"""
    st.markdown("<div class='config-section'>", unsafe_allow_html=True)
    st.markdown("<div class='config-title'>⚙️ 搜索配置</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        search_depth = st.radio(
            "📊 搜索深度",
            options=["浅度", "深度"],
            index=1,
            horizontal=True,
        )

    with col2:
        data_sources = st.radio(
            "📚 数据源",
            options=["网页", "学术"],
            index=0,
            horizontal=True,
        )

    with col3:
        report_language = st.radio(
            "🌐 报告语言",
            options=["中文", "英文"],
            index=0,
            horizontal=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    return search_depth, data_sources, report_language


def render_report_panel():
    """渲染右侧报告面板"""
    st.markdown('<div class="right-panel" style="background: white; border-radius: 12px; padding: 2rem; border: 1px solid #e0e0e0; min-height: 500px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.3rem; font-weight: 600; color: #1a1a1a; margin-bottom: 1.5rem; padding-bottom: 0.8rem; border-bottom: 2px solid #1E88E5;">📋 调研报告</div>', unsafe_allow_html=True)

    if not st.session_state.report:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">等待调研</div>
            <div style="font-size: 0.9rem;">请在左侧输入调研主题，点击「开始调研」按钮</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 显示报告内容
        st.markdown(st.session_state.report)

        # 下载按钮
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("**📥 下载报告**")

        col1, col2, col3 = st.columns(3)

        with col1:
            if "markdown" in st.session_state.output_files:
                try:
                    with open(st.session_state.output_files["markdown"], "rb") as f:
                        st.download_button(
                            label="📄 Markdown",
                            data=f,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"读取 Markdown 文件失败: {e}")

        with col2:
            if "html" in st.session_state.output_files:
                try:
                    with open(st.session_state.output_files["html"], "rb") as f:
                        st.download_button(
                            label="🌐 HTML",
                            data=f,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"读取 HTML 文件失败: {e}")

        with col3:
            if "pdf" in st.session_state.output_files:
                try:
                    with open(st.session_state.output_files["pdf"], "rb") as f:
                        st.download_button(
                            label="📕 PDF",
                            data=f,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception:
                    st.info("💡 PDF 生成需额外依赖")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_progress_panel():
    """渲染进度面板"""
    if st.session_state.todos:
        st.markdown("---")
        st.markdown("### ✅ 任务进度")
        for i, todo in enumerate(st.session_state.todos, 1):
            st.markdown(f"**{i}.** {todo}")


def render_errors():
    """渲染错误信息"""
    if st.session_state.errors:
        st.markdown("---")
        st.markdown("### ⚠️ 处理过程中的问题")
        for error in st.session_state.errors:
            st.warning(error)


def main():
    """主函数"""
    init_session_state()

    # 检查 API Key
    if not settings.deepseek_api_key:
        st.error("❌ 请在 `.env` 文件中配置 `DEEPSEEK_API_KEY`")
        st.code("DEEPSEEK_API_KEY=your_api_key_here")
        st.info("获取 API Key: https://platform.deepseek.com/")
        st.stop()

    # 显示 API 状态提示
    st.sidebar.markdown("### ⚙️ API 状态")
    st.sidebar.markdown(f"✅ DeepSeek: 已配置")

    # 检查 Tavily API Key
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if tavily_key and tavily_key != "your_tavily_api_key_here":
        st.sidebar.markdown(f"✅ Tavily 搜索: 已配置")
    else:
        st.sidebar.markdown(f"❌ Tavily 搜索: 未配置")
        st.sidebar.markdown("👉 [获取 Tavily API Key](https://tavily.com/)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 使用说明")
    st.sidebar.markdown("""
    1. 输入要调研的主题
    2. 选择搜索深度
    3. 点击「开始调研」
    4. 等待报告生成
    5. 下载 MD/HTML 格式

    **必需配置**:
    - DeepSeek API Key
    - Tavily API Key
    """)

    # 主布局：左右分栏
    col_left, col_right = st.columns([2, 5], gap="medium")

    with col_left:
        # 左侧面板
        render_header()
        query = render_input_area()
        search_depth, data_sources, report_language = render_config_options()

        st.markdown("")

        # 开始按钮
        start_button = st.button(
            "🚀 开始调研",
            disabled=st.session_state.is_running,
            use_container_width=True,
        )

        # 显示进度
        if st.session_state.todos:
            render_progress_panel()

        # 显示错误
        render_errors()

    with col_right:
        # 右侧报告面板
        render_report_panel()

    # 处理开始调研
    if start_button and query:
        st.session_state.is_running = True
        st.session_state.query = query
        st.session_state.errors = []

        # 创建进度显示
        progress_bar = st.progress(0, text="准备开始...")

        try:
            # 运行工作流
            output_dir = os.path.join(os.path.dirname(__file__), "outputs")

            progress_bar.progress(10, text="📋 拆解任务中...")
            progress_bar.progress(30, text="🔍 执行搜索中...")
            progress_bar.progress(50, text="🔬 分析内容中...")
            progress_bar.progress(70, text="📊 撰写报告中...")
            progress_bar.progress(90, text="✅ 验证报告中...")

            # 执行实际工作流
            result = run_deepfind_workflow(query, output_dir)

            progress_bar.progress(100, text="🎉 调研完成！")

            # 更新状态
            st.session_state.todos = result.get("todos", [])
            st.session_state.report = result.get("report", "")
            st.session_state.sources = result.get("sources", [])
            st.session_state.output_files = result.get("output_files", {})
            st.session_state.errors = result.get("errors", [])

            # 显示验证结果
            verification = result.get("verification", {})
            if verification:
                if verification.get("passed"):
                    st.success(f"✅ 报告验证通过 (得分: {verification.get('score', 0)}/100)")
                else:
                    st.warning(f"⚠️ 报告可能不完整 (得分: {verification.get('score', 0)}/100)")
                    for issue in verification.get("issues", []):
                        st.warning(f"  - {issue}")

        except Exception as e:
            logger.error(f"调研过程出错: {str(e)}")
            st.error(f"❌ 调研过程出错: {str(e)}")
            st.session_state.errors.append(str(e))

            with st.expander("查看错误详情"):
                import traceback
                st.code(traceback.format_exc(), language="python")

        finally:
            st.session_state.is_running = False
            st.rerun()


if __name__ == "__main__":
    main()