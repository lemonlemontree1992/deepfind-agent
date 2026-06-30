"""配置管理模块"""

import os
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    # API Keys
    deepseek_api_key: str = ""
    brave_search_api_key: str = ""

    # 搜索配置
    search_depth: Literal["shallow", "deep"] = "deep"
    max_search_results: int = 10
    default_language: Literal["zh", "en"] = "zh"

    # 模型配置
    deepseek_model: str = "deepseek-chat"  # 使用快速模型（性能提升75%）
    deepseek_model_for_research: str = "deepseek-reasoner"  # 深度调研场景使用推理模型
    deepseek_temperature: float = 0.7

    # 报告生成配置
    report_mode: Literal["basic", "enhanced"] = "basic"  # basic: 基础版, enhanced: 增强版（多阶段生成）
    report_max_sources: int = 8  # 报告中使用的最大来源数量

    # 网页解析配置
    jina_reader_timeout: int = 15  # 与 web_scraper.py 保持一致
    playwright_timeout: int = 20000  # 与 web_scraper.py 保持一致

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从环境变量读取配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")

        # 搜索配置
        search_depth_env = os.getenv("SEARCH_DEPTH", "deep")
        if search_depth_env in ("shallow", "deep"):
            self.search_depth = search_depth_env

        max_results_env = os.getenv("MAX_SEARCH_RESULTS", "10")
        try:
            self.max_search_results = int(max_results_env)
        except ValueError:
            self.max_search_results = 10

        language_env = os.getenv("DEFAULT_LANGUAGE", "zh")
        if language_env in ("zh", "en"):
            self.default_language = language_env

        # 报告生成配置
        report_mode_env = os.getenv("REPORT_MODE", "basic")
        if report_mode_env in ("basic", "enhanced"):
            self.report_mode = report_mode_env

        max_sources_env = os.getenv("REPORT_MAX_SOURCES", "8")
        try:
            self.report_max_sources = int(max_sources_env)
        except ValueError:
            self.report_max_sources = 8


settings = Settings()