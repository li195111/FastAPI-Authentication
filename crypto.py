'''
Crypto Module
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from passlib.context import CryptContext

crypt_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
  return crypt_ctx.verify(plain_password, hashed_password)


def hashing_pswd(password):
  return crypt_ctx.hash(password)
