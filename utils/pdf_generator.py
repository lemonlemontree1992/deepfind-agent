"""PDF 生成工具"""

import os
import platform
import logging
from typing import Optional
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

WEASYPRINT_AVAILABLE = False
REPORTLAB_AVAILABLE = False

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except Exception as e:
    logger.debug(f"WeasyPrint not available: {e}")

# 跨平台字体发现
def find_chinese_fonts() -> dict:
    """跨平台发现中文字体"""
    system = platform.system()
    fonts = {}

    # 常见中文字体路径
    font_paths = {
        'Darwin': {  # macOS
            'SimSun': [
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/Supplemental/Songti.ttc',
            ],
            'SimHei': [
                '/System/Library/Fonts/STHeiti Medium.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/Supplemental/Songti.ttc',
            ]
        },
        'Linux': {
            'SimSun': [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            ],
            'SimHei': [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
            ]
        },
        'Windows': {
            'SimSun': [
                'C:/Windows/Fonts/simsun.ttc',
                'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑作为备选
            ],
            'SimHei': [
                'C:/Windows/Fonts/simhei.ttf',
                'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑作为备选
            ]
        }
    }

    system_fonts = font_paths.get(system, {})
    for font_name, paths in system_fonts.items():
        for path in paths:
            if os.path.exists(path):
                fonts[font_name] = path
                break

    return fonts


CHINESE_FONTS = find_chinese_fonts()

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True

    # 注册中文字体（跨平台）
    CHINESE_FONT_AVAILABLE = False
    try:
        if 'SimSun' in CHINESE_FONTS:
            pdfmetrics.registerFont(TTFont('SimSun', CHINESE_FONTS['SimSun']))
        if 'SimHei' in CHINESE_FONTS:
            pdfmetrics.registerFont(TTFont('SimHei', CHINESE_FONTS['SimHei']))
        CHINESE_FONT_AVAILABLE = bool(CHINESE_FONTS)
        if CHINESE_FONT_AVAILABLE:
            logger.info(f"中文字体注册成功: {CHINESE_FONTS}")
        else:
            logger.warning("未找到中文字体，PDF 生成可能无法正确显示中文")
    except Exception as e:
        logger.warning(f"中文字体注册失败: {e}")
        CHINESE_FONT_AVAILABLE = False
except Exception as e:
    logger.debug(f"ReportLab not available: {e}")
    REPORTLAB_AVAILABLE = False
    CHINESE_FONT_AVAILABLE = False

import markdown
from markdown.extensions.tables import TableExtension


def markdown_to_html(md_content: str, title: str = "调研报告") -> str:
    """将 Markdown 转换为 HTML"""
    html_content = markdown.markdown(
        md_content,
        extensions=[TableExtension(), "fenced_code", "toc"]
    )

    full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
        }}
        h1 {{
            font-size: 28px;
            border-bottom: 2px solid #1E88E5;
            padding-bottom: 15px;
            margin-top: 30px;
        }}
        h2 {{
            font-size: 22px;
            color: #1565C0;
            margin-top: 30px;
            border-left: 4px solid #1E88E5;
            padding-left: 15px;
        }}
        h3 {{
            font-size: 18px;
            color: #1976D2;
            margin-top: 25px;
        }}
        p {{
            text-align: justify;
            margin: 15px 0;
        }}
        a {{
            color: #1E88E5;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SF Mono", Consolas, monospace;
        }}
        blockquote {{
            border-left: 4px solid #90CAF9;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 30px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #1E88E5;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .source {{
            color: #888;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
    <div class="source">
        <p>📋 此报告由 DeepFind Agent 自动生成</p>
        <p>⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
    return full_html


def markdown_to_pdf_weasyprint(md_content: str, output_path: str, title: str = "调研报告") -> bool:
    """使用 WeasyPrint 将 Markdown 转换为 PDF"""
    if not WEASYPRINT_AVAILABLE:
        return False

    try:
        html_content = markdown_to_html(md_content, title)
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        html.write_pdf(output_path, font_config=font_config)
        return True
    except Exception as e:
        logger.error(f"WeasyPrint PDF 生成失败: {e}")
        return False


def markdown_to_pdf_reportlab(md_content: str, output_path: str, title: str = "调研报告") -> bool:
    """使用 ReportLab 将 Markdown 转换为 PDF"""
    if not REPORTLAB_AVAILABLE:
        return False

    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        # 创建中文样式
        font_name = "SimSun" if CHINESE_FONT_AVAILABLE else "Helvetica"
        styles.add(ParagraphStyle(
            name="Chinese",
            fontName=font_name,
            fontSize=12,
            leading=20,
        ))
        styles.add(ParagraphStyle(
            name="ChineseTitle",
            fontName=font_name,
            fontSize=24,
            leading=30,
            spaceAfter=20,
        ))
        styles.add(ParagraphStyle(
            name="ChineseH2",
            fontName=font_name,
            fontSize=16,
            leading=24,
            spaceBefore=15,
            spaceAfter=10,
        ))

        story = []

        # 处理 Markdown 内容
        lines = md_content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 跳过 Markdown 标记符号
            clean_line = line.replace("**", "").replace("`", "").replace("*", "")

            if line.startswith("# "):
                story.append(Paragraph(clean_line[2:], styles["ChineseTitle"]))
            elif line.startswith("## "):
                story.append(Paragraph(clean_line[3:], styles["ChineseH2"]))
            elif line.startswith("---"):
                story.append(Spacer(1, 0.5 * cm))
            else:
                story.append(Paragraph(clean_line, styles["Chinese"]))
                story.append(Spacer(1, 0.3 * cm))

        doc.build(story)
        return True
    except Exception as e:
        logger.error(f"ReportLab PDF 生成失败: {e}")
        return False


def generate_pdf(md_content: str, output_path: str, title: str = "调研报告") -> bool:
    """生成 PDF（自动选择可用方法）"""
    # 优先使用 WeasyPrint
    if WEASYPRINT_AVAILABLE:
        if markdown_to_pdf_weasyprint(md_content, output_path, title):
            return True

    # 备用 ReportLab
    if REPORTLAB_AVAILABLE:
        if markdown_to_pdf_reportlab(md_content, output_path, title):
            return True

    logger.warning("PDF 生成库不可用，请安装: pip install weasyprint 或 pip install reportlab")
    return False


def generate_html(md_content: str, output_path: str, title: str = "调研报告") -> bool:
    """生成 HTML 文件（作为 PDF 的备选）"""
    try:
        html_content = markdown_to_html(md_content, title)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
    except Exception as e:
        logger.error(f"HTML 文件生成失败: {e}")
        return False


def generate_markdown_file(content: str, output_path: str) -> bool:
    """生成 Markdown 文件"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Markdown 文件生成失败: {e}")
        return False