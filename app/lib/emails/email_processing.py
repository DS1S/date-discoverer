from fastapi import HTTPException, status

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape
)

from app.settings import settings


def send_templated_email(template, subject, to, **kwargs):
    env = Environment(
        loader=FileSystemLoader('app/email_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template)
    _send_email(to, subject, template.render(**kwargs))


def _send_email(to, subj, body):

    msg = MIMEMultipart('alternative')
    msg['From'] = settings.GMAIL_USER
    msg['Subject'] = subj
    msg['To'] = ','.join(to)

    msg.attach(MIMEText(body, 'html', 'utf-8'))

    smtp = None
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(settings.GMAIL_USER, settings.GMAIL_PASSWORD)
        smtp.sendmail(settings.GMAIL_USER, to, msg.as_string())
    except smtplib.SMTPException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    finally:
        if smtp:
            smtp.quit()
