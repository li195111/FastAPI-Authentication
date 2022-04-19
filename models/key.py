'''
Key Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import pydantic
import jwcrypto.jwk

from .base import IBase


class Key(IBase):
  key: str | dict | jwcrypto.jwk.JWK

  @pydantic.validator('key')
  def valid_key(cls, v: dict | jwcrypto.jwk.JWK):
    if isinstance(v, dict):
      return jwcrypto.jwk.JWK(**v)
    return v


class PrivateKey(Key):
  exp: float


class PublicKey(Key):
  exp: float


class AuthKeys(IBase):
  kid: str
  pvk: PrivateKey
  pbk: PublicKey
