'''Email Validation'''
from datetime import datetime, timedelta

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from string import Template

import dependencies
import models
import utils

secret = {
    'green07111@gmail.com': 'kjwzvaprfllzdapz',
    'a0983953000@gmail.com': 'jbhnyfmbcsthaukx'
}


def validation_mail(opts, user: models.SQLUser, key):
  content = MIMEMultipart()
  content['subject'] = '驗證您的QChoice帳戶'  # 標題
  content['from'] = 'green07111@gmail.com'  # 寄件者
  content['to'] = user.email  # 收件者
  front_host = f'{opts.front_host}:{opts.front_port}'
  if opts.front_dns:
    front_host = opts.front_dns
  exp_delta = timedelta(hours=24)
  keys_gen = dependencies.get_keys(opts)
  for keys in keys_gen:
    claims = {
        'sub': user.email,
        'key': keys.pbk.key,
        'exp': (datetime.utcnow() + exp_delta).timestamp() * 1000
    }
    token = dependencies.jose_token_encode(opts, claims, key)

  # 郵件內容
  with open('sample.html', 'r', encoding='utf-8') as fp:
    template = Template(fp.read())
  body = template.substitute({
      'user':
      user.full_name,
      'url':
      f'http://{front_host}/validation?token={token}'
  })

  # HTML內容
  content.attach(MIMEText(body, 'html'))

  # 設定 SMTP 伺服器
  with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
    # 驗證 SMTP 伺服器
    smtp.ehlo()
    # 建立加密傳輸
    smtp.starttls()
    # 登入寄件者 Email
    smtp.login(content['from'], opts.email_secret)
    # 寄送郵件
    smtp.send_message(content)


def send_validation(opts, db_user, key):
  try:
    validation_mail(opts, db_user, key)
  except Exception as e:
    if opts.debug:
      return utils.error_msg(e).details_message
  return ''
