import enum
from typing import Any

import pydantic
from jwcrypto import jwk

from utils import utc_now


class Status(enum.Enum):
  Failed = 'failed'
  Success = 'success'

  def __repr__(self) -> str:
    return self.value


class IBase(pydantic.BaseModel):

  def __init__(__pydantic_self__, **data: Any) -> None:
    super().__init__(**data)


class IResponse(IBase):
  '''Response Interface'''
  status: Status
  time: str = ''
  msg: str = ''

  def __init__(__pydantic_self__, **data: Any) -> None:
    if not 'time' in data:
      data['time'] = utc_now()
    super().__init__(**data)


class PrivateKey(IBase):
  pvk: jwk.JWK
  exp: float


class PublicKey(IBase):
  pbk: str | dict
  exp: float


class AuthKeys(IBase):
  kid: str
  pvk: str | dict
  pbk: str | dict


class Response(IResponse):

  def __init__(__pydantic_self__, **data: Any) -> None:
    super().__init__(**data)


class AuthResponse(IResponse):
  token: str
  kid: str
  key: PrivateKey | PublicKey
  verify: bool = False

  def __init__(__pydantic_self__, **data: Any) -> None:
    super().__init__(**data)


class User(IBase):
  username: str
  email: str | None = None
  full_name: str | None = None
  disable: bool | None = None


class UserInDB(User):
  hashed_password: str


class Token(IBase):
  access_token: str
  token_type: str


class TokenData(IBase):
  username: str | None = None
