"""统一的 LLM 客户端 - 带重试和速率限制"""

import time
import logging
from typing import Optional
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage

from config import settings

logger = logging.getLogger(__name__)


class RateLimitedLLM:
    """带速率限制的 LLM 客户端"""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3,
        min_interval: float = 1.0,  # 最小请求间隔（秒）
    ):
        """
        初始化带速率限制的 LLM 客户端

        Args:
            model: 模型名称，默认使用 settings.deepseek_model
            temperature: 温度参数
            max_retries: 最大重试次数
            min_interval: 最小请求间隔
        """
        self.model = model or settings.deepseek_model
        self.temperature = temperature
        self.max_retries = max_retries
        self.min_interval = min_interval
        self._last_request_time = 0

        # 创建 LLM 实例
        self.llm = ChatDeepSeek(
            model=self.model,
            temperature=self.temperature,
            api_key=settings.deepseek_api_key,
        )

    def _wait_for_rate_limit(self):
        """等待速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"速率限制等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)

    def invoke(
        self,
        messages,
        retry_on_rate_limit: bool = True,
        **kwargs
    ):
        """
        调用 LLM，带重试机制

        Args:
            messages: 消息列表
            retry_on_rate_limit: 遇到速率限制时是否重试
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # 等待速率限制
                self._wait_for_rate_limit()

                # 调用 LLM
                self._last_request_time = time.time()
                response = self.llm.invoke(messages, **kwargs)

                return response

            except Exception as e:
                error_str = str(e)
                last_exception = e

                # 检查是否是速率限制错误 (429)
                if "429" in error_str or "rate limit" in error_str.lower() or "限流" in error_str:
                    if retry_on_rate_limit and attempt < self.max_retries - 1:
                        # 指数退避
                        wait_time = (2 ** attempt) * 2 + 1  # 3, 5, 9 秒
                        logger.warning(f"遇到速率限制 (429)，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"速率限制重试失败，已达到最大重试次数 ({self.max_retries})")
                        raise

                # 其他错误直接抛出
                logger.error(f"LLM 调用失败: {error_str}")
                raise

        # 所有重试都失败
        raise last_exception


# 全局缓存，避免重复创建实例
_llm_cache = {}


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    use_rate_limit: bool = True,
) -> RateLimitedLLM:
    """
    获取 LLM 客户端实例（带缓存）

    Args:
        model: 模型名称
        temperature: 温度参数
        use_rate_limit: 是否使用速率限制

    Returns:
        RateLimitedLLM 实例
    """
    model = model or settings.deepseek_model
    cache_key = f"{model}_{temperature}_{use_rate_limit}"

    if cache_key not in _llm_cache:
        if use_rate_limit:
            _llm_cache[cache_key] = RateLimitedLLM(
                model=model,
                temperature=temperature,
            )
        else:
            # 不使用速率限制的快速客户端
            _llm_cache[cache_key] = ChatDeepSeek(
                model=model,
                temperature=temperature,
                api_key=settings.deepseek_api_key,
            )

    return _llm_cache[cache_key]