from unittest import TestCase
from smtplib import SMTP
from app.sdk.email import *
from app.core import config

SEND_DEST = "bail@bail.asia"

def send_mail(smtp: SMTP):
    smtp.sendmail(
        from_addr=config.settings.smtp_username,
        to_addrs=SEND_DEST,
        msg=f"""FROM: {config.settings.email_from} <{config.settings.smtp_username}>
TO: <bail@bail.asia>
SUBJECT: test_email_from_{config.settings.smtp_encryption}
MIME-Version: 1.0
Content-type: text/html

hello"""
    )
    smtp.quit()
    smtp.close()


# class TestGetEmailClient(TestCase):
#     def test_get_ssl_smtp_client(self):
#         config.settings.smtp_port = 465
#         config.settings.smtp_encryption = config.SmtpEncryption.SSL
#         smtp_client = get_smtp_client()
#         send_mail(smtp_client)
#         self.assertTrue(input('请手动评判 >'))

#     def test_get_tls_smtp_client(self):
#         config.settings.smtp_port = 587
#         config.settings.smtp_encryption = config.SmtpEncryption.STARTTLS
#         smtp_client = get_smtp_client()
#         send_mail(smtp_client)
#         self.assertTrue(input('请手动评判 >'))

class TestSendEmail(TestCase):
    def test_send_email(self):
        send([SEND_DEST, '2915289604@qq.com'], 'critical', '<script>alert("xss")</script>')
        self.assertTrue(input('请手动评判 >'))
