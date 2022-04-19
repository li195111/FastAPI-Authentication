'''
Response Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from typing import Any

import utils
from .base import IBase
from .enums import Status
from .key import Key


# Response
class IResponse(IBase):
  '''Response Interface'''
  status: Status
  time: str = ''
  msg: str = ''

  def __init__(self, **data: Any) -> None:
    if 'time' not in data:
      data['time'] = utils.utc_now()
    super().__init__(**data)


class Auth(IBase):
  token: str
  key: dict
  kid: str


class Verify(Key):
  sub: str
