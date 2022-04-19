'''
Utils Module 
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import datetime
import sys
import traceback
import uuid


class ErrorMessage:
  '''Error Message Instanace'''

  def __init__(self, error_class, detail, file_track) -> None:
    self.error_class = error_class
    self.detail = detail
    self.file_track = file_track

  def __str__(self) -> str:
    return self.part_message

  @property
  def part_message(self):
    return f'[{self.error_class}] {self.detail}'

  @property
  def details_message(self):
    return f'\n{self.file_track}\n[{self.error_class}] {self.detail}\n'


def error_msg(err):
  error_class = err.__class__.__name__
  if len(err.args) > 0:
    detail = err.args[0]
  else:
    detail = ''
  _, _, tb = sys.exc_info()
  details = '\n'.join([
      f'File \'{s[0]}\', line {s[1]} in {s[2]}'
      for s in traceback.extract_tb(tb)
  ])
  return ErrorMessage(error_class, detail, details)


def utc_now() -> str:
  return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')


def uuidgen() -> str:
  return uuid.uuid4().hex
