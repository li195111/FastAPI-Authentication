'''
User Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import re
import uuid
import datetime

import pydantic

from .base import IBase
from .items import Item
from .key import Key
import crypto


# Login Active
class LoginActive(IBase):
  ip_address: str
  user_agent: str


# User
class IUser(IBase):
  pass


class Guest(IUser):
  uid: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
  permission: int = 1


class ValidationUser(Key):
  sub: str
  exp: datetime.datetime | None = None

  @pydantic.validator('sub')
  def valid_sub(cls, v: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    assert re.fullmatch(regex, v), ValueError('invalid sub')
    return v


class RegisteredUser(IUser):
  '''Registered User Model'''
  full_name: str = ''
  sub: str

  @pydantic.validator('sub')
  def valid_sub(cls, v: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    assert re.fullmatch(regex, v), ValueError('invalid sub')
    return v


class OAuth2UserForm(RegisteredUser):
  grant_type: str
  password: str
  scope: str = ''
  client_id: str | None = None
  client_secret: str | None = None

  class Config:
    orm_mode = True


class OAuth2UserFormWithKey(Key):
  form: OAuth2UserForm


class UserCreate(RegisteredUser):
  '''User Create Model'''
  password: str
  salt: str = ''
  iter: int = 0
  keylen: int = 0
  digest: str = ''

  @pydantic.validator('password')
  def valid_pswd(cls, v: str):
    return crypto.hashing_pswd(v)


class UserCreateWithKey(Key):
  user_create: UserCreate


class UserInfo(RegisteredUser):
  uid: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
  items: list[Item] = []

  class Config:
    orm_mode = True


class User(RegisteredUser):
  '''User Model'''
  uid: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
  permission: int = 1
  salt: str = ''
  iter: int = 0
  keylen: int = 0
  digest: str = ''
  password: str
  id: int | None
  items: list[Item] = []
  create: datetime.datetime = pydantic.Field(
      default_factory=datetime.datetime.utcnow)
  is_active: bool = False

  class Config:
    orm_mode = True


class UserWithKey(Key):
  user: User
