'''
Token Dependencies
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import uuid
from datetime import datetime, timedelta

import jwcrypto.jwt
import jwcrypto.jwk
import jose.jwt

import database
import models


def verify_token_manager(token: str):
  return len(token) == 32


def generate_auth_key(opts, exp_delta=timedelta(days=7)):
  kid = uuid.uuid4().hex
  pvk = jwcrypto.jwk.JWK.generate(kty=opts.jwk_kty,
                                  size=opts.jwk_size,
                                  kid=kid)
  exp_time = (datetime.utcnow() + exp_delta).timestamp() * 1000
  return models.AuthKeys(kid=kid,
                         pvk=models.PrivateKey(key=pvk.export_private(True),
                                               exp=exp_time),
                         pbk=models.PublicKey(key=pvk.export_public(True),
                                              exp=exp_time))


def get_keys(opts):
  for rdb in database.get_rdb():
    pvk_str = rdb.hget('PV_KEYS', opts.kid)
    pbk_str = rdb.hget('PB_KEYS', opts.kid)
    pvk_obj = models.PrivateKey.parse_raw(pvk_str)
    pbk_obj = models.PublicKey.parse_raw(pbk_str)
    if datetime.utcnow().timestamp() * 1000 > pvk_obj.exp:
      key = generate_auth_key(opts, timedelta(days=opts.jwt_exp_days))
      update_auth_key(key)
      opts.kid = key.kid
      pvk = key.pvk
      pbk = key.pbk
    else:
      pvk = pvk_obj
      pbk = pbk_obj
    yield models.AuthKeys(kid=opts.kid, pvk=pvk, pbk=pbk)


def get_auth(opts, exp_delta=timedelta(seconds=3)):
  for keys in get_keys(opts):
    exp_time = (datetime.utcnow() + exp_delta).timestamp() * 1000
    jwt_claims = {'exp': exp_time}
    encoded_jwt = jwcrypto.jwt.JWT(header=opts.jwt_header, claims=jwt_claims)
    encoded_jwt.make_encrypted_token(jwcrypto.jwk.JWK(**keys.pvk.key))
    yield models.Auth(token=encoded_jwt.serialize(),
                      key=keys.pbk.key,
                      kid=opts.kid)


def update_auth_key(key: models.AuthKeys):
  for rdb in database.get_rdb():
    rdb.hset('PV_KEYS', key.kid, key.pvk.json())
    rdb.hset('PB_KEYS', key.kid, key.pbk.json())


def token_encode(opts, claims, key):
  encoded_jwt = jwcrypto.jwt.JWT(header=opts.jwt_header, claims=claims)
  encoded_jwt.make_encrypted_token(key)
  return encoded_jwt.serialize()


def token_decode(opts, token, key=None):
  for rdb in database.get_rdb():
    if key is None:
      pvk_str = rdb.hget('PV_KEYS', opts.kid)
      pvk_obj = models.PrivateKey.parse_raw(pvk_str)
      key = jwcrypto.jwk.JWK(**pvk_obj.key)
    jwt_obj = jwcrypto.jwt.JWT()
    jwt_obj.deserialize(token, key)
    yield jwt_obj.claims


def jose_token_encode(opts, claims, key):
  return jose.jwt.encode(claims, key, algorithm=opts.jwt_access_alg)


def jose_token_decode(opts, token, key):
  return jose.jwt.decode(token, key, algorithms=[opts.jwt_access_alg])


def create_access_token(opts,
                        claims: dict,
                        exp_delta: timedelta = timedelta(minutes=15)):
  claims.update({'exp': (datetime.utcnow() + exp_delta).timestamp() * 1000})
  for keys in get_keys(opts):
    yield token_encode(opts, claims, keys.pbk.key)
