"""网页解析工具 - Jina Reader + Playwright（优化版）"""

import logging
import os
import httpx
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 可配置超时参数
JINA_TIMEOUT = float(os.getenv("JINA_TIMEOUT", "15.0"))
PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "20000"))
MAX_WORKERS = int(os.getenv("SCRAPER_MAX_WORKERS", "5"))

# 全局共享 HTTP 客户端（带连接池）
_shared_client: Optional[httpx.Client] = None


def get_shared_client() -> httpx.Client:
    """获取共享的 HTTP 客户端实例（带连接池）"""
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.Client(
            timeout=httpx.Timeout(JINA_TIMEOUT, connect=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            follow_redirects=True
        )
    return _shared_client


def close_shared_client():
    """关闭共享 HTTP 客户端"""
    global _shared_client
    if _shared_client:
        _shared_client.close()
        _shared_client = None


def jina_reader_sync(url: str) -> Dict[str, Any]:
    """
    使用 Jina Reader 解析网页内容（免费，无需 API Key）

    优化：使用共享连接池，超时时间可配置

    Args:
        url: 要解析的网页 URL

    Returns:
        包含 title, content, url, source 的字典
        如果解析失败，返回包含 error 字段的字典
    """
    jina_url = f"https://r.jina.ai/{url}"

    try:
        logger.info(f"Jina Reader 解析: {url}")

        client = get_shared_client()
        response = client.get(jina_url)
        response.raise_for_status()
        content = response.text

        title = _extract_title(content, url)

        logger.info(f"Jina Reader 解析成功，内容长度: {len(content)}")

        return {
            "title": title,
            "content": content,
            "url": url,
            "source": "jina_reader",
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Jina Reader HTTP 错误: {e.response.status_code}")
        return {"error": f"HTTP {e.response.status_code}", "url": url}
    except httpx.TimeoutException:
        logger.error(f"Jina Reader 超时 ({JINA_TIMEOUT}s): {url}")
        return {"error": "请求超时", "url": url}
    except Exception as e:
        logger.error(f"Jina Reader 解析失败: {str(e)}")
        return {"error": str(e), "url": url}


def _extract_title(content: str, url: str) -> str:
    """从内容中提取标题"""
    lines = content.split("\n")
    for line in lines[:10]:  # 只检查前10行
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("title:"):
            return line[6:].strip()
    # 从 URL 提取
    return url.split("/")[-1].replace("-", " ").title() if url else "Unknown"


def playwright_scraper_sync(url: str) -> Dict[str, Any]:
    """
    使用 Playwright 解析动态网页内容（备用方案）

    适用于 JavaScript 渲染的页面

    Args:
        url: 要解析的网页 URL

    Returns:
        包含 title, content, url, source 的字典
    """
    try:
        logger.info(f"Playwright 解析: {url}")

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(url, timeout=PLAYWRIGHT_TIMEOUT, wait_until="domcontentloaded")
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as e:
                logger.warning(f"Playwright 页面加载警告: {str(e)}")

            title = page.title()
            content = page.content()

            # 使用 BeautifulSoup 清理 HTML
            soup = BeautifulSoup(content, "html.parser")

            # 移除不需要的元素
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)

            browser.close()

            logger.info(f"Playwright 解析成功，内容长度: {len(text)}")

            return {
                "title": title,
                "content": text,
                "url": url,
                "source": "playwright",
            }

    except Exception as e:
        logger.error(f"Playwright 解析失败: {str(e)}")
        return {"error": str(e), "url": url}


def scrape_url(url: str, prefer_jina: bool = True) -> Dict[str, Any]:
    """
    智能选择解析方式

    Args:
        url: 网页 URL
        prefer_jina: 是否优先使用 Jina Reader

    Returns:
        解析结果字典
    """
    if prefer_jina:
        result = jina_reader_sync(url)
        if "error" not in result:
            return result
        logger.warning(f"Jina Reader 失败，尝试 Playwright: {result.get('error')}")

    # Jina 失败，尝试 Playwright
    return playwright_scraper_sync(url)


def scrape_urls_parallel(urls: List[str], max_workers: int = MAX_WORKERS) -> List[Dict[str, Any]]:
    """
    并行解析多个 URL

    Args:
        urls: URL 列表
        max_workers: 最大并行线程数

    Returns:
        解析结果列表
    """
    logger.info(f"开始并行解析 {len(urls)} 个 URL，最大并行数: {max_workers}")

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_url = {
            executor.submit(scrape_url, url): url
            for url in urls
        }

        # 收集结果
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                if "error" not in result:
                    logger.info(f"✓ 解析成功: {url[:50]}...")
                else:
                    logger.warning(f"✗ 解析失败: {url[:50]}... - {result.get('error')}")
            except Exception as e:
                logger.error(f"解析异常: {url} - {str(e)}")
                results.append({"error": str(e), "url": url})

    # 统计成功数量
    success_count = sum(1 for r in results if "error" not in r)
    logger.info(f"并行解析完成，成功: {success_count}/{len(urls)}")

    return results


def scrape_urls_sequential(urls: List[str]) -> List[Dict[str, Any]]:
    """
    顺序解析多个 URL（备用方案，稳定性更高）

    Args:
        urls: URL 列表

    Returns:
        解析结果列表
    """
    logger.info(f"开始顺序解析 {len(urls)} 个 URL")

    results = []
    for i, url in enumerate(urls, 1):
        logger.info(f"解析进度: {i}/{len(urls)}")
        result = scrape_url(url)
        results.append(result)

        if "error" not in result:
            logger.info(f"✓ 解析成功: {url[:50]}...")
        else:
            logger.warning(f"✗ 解析失败: {url[:50]}...")

    success_count = sum(1 for r in results if "error" not in r)
    logger.info(f"顺序解析完成，成功: {success_count}/{len(urls)}")

    return results