import smtplib
from email.mime.text import MIMEText
from email.header import Header
from trybar.settings import MAIL_FROM, MAIL_FRIENDLY_FROM, MAIL_USER, MAIL_PASS, \
                            MAIL_SERVER, MAIL_PORT
def send_mail(target, title, content):
    msg = MIMEText(content, 'plain', 'utf8')
    msg['Subject'] = Header(title.encode('utf8'), 'utf8')
    msg['From'] = MAIL_FROM
    msg['To'] = target

    s = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    s.login(MAIL_USER, MAIL_PASS)
    s.sendmail(MAIL_FROM, [target], msg.as_string())
    s.quit()
