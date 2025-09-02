from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
import jinja2
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
    <title>代码评审结果</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            padding: 20px 30px;
            color: white;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .content {
            padding: 30px;
        }
        .risk-level {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .risk-level.critical {
            background-color: #fee;
            color: #c00;
            border: 1px solid #fcc;
        }
        .risk-level.high {
            background-color: #fff3e0;
            color: #e65100;
            border: 1px solid #ffcc80;
        }
        .risk-level.medium {
            background-color: #fff8e1;
            color: #f57f17;
            border: 1px solid #ffecb3;
        }
        .risk-level.low {
            background-color: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #a5d6a7;
        }
        .review-result {
            background-color: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }
        .review-result pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', Courier, monospace;
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #777;
            font-size: 12px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>代码评审结果通知</h1>
        </div>
        <div class="content">
            <h2>评审详情</h2>
            
            <div>
                <strong>风险等级:</strong>
                <div class="risk-level {{ risk_level.lower() }}">
                    {{ risk_level }}
                </div>
            </div>
            
            <div>
                <strong>评审结果:</strong>
                <div class="review-result">
                    {{ review_result }}
                </div>
            </div>
            
            <p>请及时处理相关问题，确保代码质量和系统安全。</p>
        </div>
        <div class="footer">
            <p>此邮件由代码评审系统自动发送，请勿回复。</p>
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
    msg['Subject'] = f'Gitlab代码评析报告'

    smtp = get_smtp_client()
    smtp.sendmail(
        from_addr=settings.smtp_username,
        to_addrs=to,
        msg=msg.as_string(),
    )


def _render_template(level: str, message: str) -> str:
    return TEMPLATE.render(
        risk_level=level,
        review_result=message,
    )
