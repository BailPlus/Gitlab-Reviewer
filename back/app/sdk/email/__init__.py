from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
import jinja2
import markdown
from ...core.config import settings, SmtpEncryption

__all__ = [
    'get_smtp_client',
    'send',
]

TEMPLATE = jinja2.Template("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitLab 代码评审结果</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #f8f9fa;
            min-height: 100vh;
            padding: 20px;
        }
        
        .email-container {
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            overflow: hidden;
        }
        
        .header {
            background: #FC6D26;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }
        
        .gitlab-logo {
            display: inline-block;
            margin-bottom: 15px;
        }
        
        .gitlab-logo svg {
            width: 40px;
            height: 40px;
            fill: white;
        }
        
        .header h1 {
            color: white;
            font-size: 24px;
            font-weight: 600;
            margin: 0;
        }
        
        .header .subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            margin-top: 8px;
            font-weight: 400;
        }
        
        .content {
            padding: 40px;
            background: #ffffff;
        }
        
        .section {
            margin-bottom: 32px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 16px;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 8px;
        }
        
        .risk-level {
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 12px;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .risk-level.critical {
            background: #dc3545;
            color: white;
        }
        
        .risk-level.high {
            background: #fd7e14;
            color: white;
        }
        
        .risk-level.medium {
            background: #ffc107;
            color: #000;
        }
        
        .risk-level.low {
            background: #28a745;
            color: white;
        }
        
        .review-result {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 24px;
            margin: 20px 0;
        }
        
        /* Markdown 样式 */
        .markdown-content {
            font-size: 14px;
            line-height: 1.6;
        }
        
        .markdown-content h1,
        .markdown-content h2,
        .markdown-content h3,
        .markdown-content h4,
        .markdown-content h5,
        .markdown-content h6 {
            color: #1a1a1a;
            margin: 20px 0 12px 0;
            font-weight: 600;
            line-height: 1.3;
        }
        
        .markdown-content h1 { font-size: 20px; }
        .markdown-content h2 { font-size: 18px; }
        .markdown-content h3 { font-size: 16px; }
        .markdown-content h4 { font-size: 15px; }
        .markdown-content h5 { font-size: 14px; }
        .markdown-content h6 { font-size: 13px; }
        
        .markdown-content p {
            margin: 12px 0;
            color: #4a5568;
        }
        
        .markdown-content strong {
            color: #1a1a1a;
            font-weight: 600;
        }
        
        .markdown-content em {
            color: #6c757d;
            font-style: italic;
        }
        
        .markdown-content ul,
        .markdown-content ol {
            margin: 12px 0;
            padding-left: 20px;
        }
        
        .markdown-content li {
            margin: 4px 0;
            color: #4a5568;
        }
        
        .markdown-content li::marker {
            color: #FC6D26;
        }
        
        .markdown-content code {
            background: #f1f3f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            font-size: 13px;
            color: #d73a49;
        }
        
        .markdown-content pre {
            background: #f8f9fa;
            color: #495057;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid #e9ecef;
        }
        
        .markdown-content pre code {
            background: none;
            padding: 0;
            color: inherit;
            font-size: 13px;
        }
        
        .markdown-content blockquote {
            border-left: 3px solid #FC6D26;
            padding-left: 16px;
            margin: 16px 0;
            color: #6c757d;
            font-style: italic;
            background: #f8f9fa;
            padding: 12px 16px;
            border-radius: 0 4px 4px 0;
        }
        
        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #dee2e6;
        }
        
        .markdown-content th,
        .markdown-content td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .markdown-content th {
            background: #f8f9fa;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .markdown-content hr {
            border: none;
            height: 1px;
            background: #dee2e6;
            margin: 24px 0;
        }
        
        .footer {
            background: #f8f9fa;
            color: #6c757d;
            text-align: center;
            padding: 24px;
            font-size: 13px;
            border-top: 1px solid #dee2e6;
        }
        
        .footer .logo-text {
            font-weight: 600;
            color: #FC6D26;
            margin-bottom: 8px;
        }
        
        .cta-section {
            background: #FC6D26;
            color: white;
            padding: 24px;
            text-align: center;
            margin: 24px 0;
            border-radius: 6px;
        }
        
        .cta-section h3 {
            margin-bottom: 8px;
            font-size: 16px;
            font-weight: 600;
        }
        
        .cta-section p {
            opacity: 0.9;
            margin: 0;
            font-size: 14px;
        }
        
        @media (max-width: 600px) {
            .email-container {
                margin: 10px;
                border-radius: 6px;
            }
            
            .content {
                padding: 24px 16px;
            }
            
            .header {
                padding: 24px 16px;
            }
            
            .header h1 {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="gitlab-logo">
                <svg viewBox="0 0 586 559" xmlns="http://www.w3.org/2000/svg">
                    <g fill="none" fill-rule="evenodd">
                        <g fill="currentColor">
                            <path d="m461.48 301.83-17.06-52.58-33.8-104.27c-1.72-5.3-9.18-5.3-10.9 0l-33.8 104.27h-145.84l-33.8-104.27c-1.72-5.3-9.18-5.3-10.9 0l-33.8 104.27-17.06 52.58c-1.56 4.8.82 10.04 5.46 12.02l175.74 127.85 175.74-127.85c4.64-1.98 7.02-7.22 5.46-12.02z"/>
                        </g>
                    </g>
                </svg>
            </div>
            <h1>GitLab 代码评审结果</h1>
            <div class="subtitle">Code Review Results & Analysis</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">📊 评审概览</h2>
                
                <div>
                    <strong style="color: #2c3e50; font-size: 16px;">风险等级：</strong>
                    <div class="risk-level {{ risk_level.lower() }}">
                        {{ risk_level }}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">🔍 详细分析结果</h2>
                <div class="review-result">
                    <div class="markdown-content">
                        {{ review_result_html | safe }}
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h3>⚡ 行动建议</h3>
                <p>请及时查看并处理相关问题，确保代码质量和系统安全。持续的代码评审有助于提升团队整体开发效率。</p>
            </div>
        </div>
        
        <div class="footer">
            <div class="logo-text">GitLab Code Reviewer</div>
            <p>此邮件由 GitLab 代码评审系统自动发送，请勿直接回复此邮件。</p>
            <p>如有疑问，请联系开发团队或系统管理员。</p>
        </div>
    </div>
</body>
</html>
""")


def get_smtp_client() -> SMTP:
    """获取SMTP客户端"""
    match settings.smtp_encryption:
        case SmtpEncryption.NONE:
            smtp = SMTP(settings.smtp_host, settings.smtp_port)
        case SmtpEncryption.SSL:
            smtp = SMTP_SSL(settings.smtp_host, settings.smtp_port)
        case SmtpEncryption.STARTTLS:
            smtp = SMTP(settings.smtp_host, settings.smtp_port)
            smtp.starttls()
    smtp.login(settings.smtp_username, settings.smtp_password)
    return smtp


def send(to: list[str], level: str, message: str):
    msg = MIMEText(_render_template(level, message), 'html', 'utf-8')
    msg['From'] = f'{settings.email_from} <{settings.smtp_username}>'
    msg['To'] = ', '.join(to)
    msg['Subject'] = f'GitLab 代码评析报告 - {level} 级别'

    smtp = get_smtp_client()
    smtp.sendmail(
        from_addr=settings.smtp_username,
        to_addrs=to,
        msg=msg.as_string(),
    )


def _render_template(level: str, message: str) -> str:
    # 将 markdown 转换为 HTML
    review_result_html = markdown.markdown(
        message,
        extensions=[
            'markdown.extensions.tables',      # 表格支持
            'markdown.extensions.fenced_code', # 代码块支持
            'markdown.extensions.codehilite',  # 代码高亮
            'markdown.extensions.toc',         # 目录支持
            'markdown.extensions.nl2br',       # 换行支持
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': False,  # 不使用 Pygments，使用 CSS 样式
            }
        }
    )
    
    return TEMPLATE.render(
        risk_level=level,
        review_result_html=review_result_html,
    )
