'''
Token Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from .base import IBase


# Token
class AccessToken(IBase):
  access_token: str
  token_type: str


class Token(IBase):
  token: str
  detail: str = ''


class SaltToken(AccessToken):
  salt: str
