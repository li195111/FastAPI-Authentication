'''
FastAPI JWT Implements
'''
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from argparse import Namespace

import redis
import dotenv
from fastapi import Request, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwcrypto import jwe, jwk, jwt

from model import AuthResponse, PublicKey, Response, Status, PrivateKey, AuthKeys
from utils import error_msg

app = FastAPI()
origins = ['http://localhost:3001']

dotenv.load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

INPUT_OPTIONS = None


@app.exception_handler(Exception)
async def http_exception_handler(exc: Exception) -> JSONResponse:
  return JSONResponse(Response(status=Status.Failed,
                               msg=error_msg(exc).details_message),
                      status_code=404)


@app.exception_handler(jwt.JWTExpired)
async def jwt_expired_exception_handler(exc: jwt.JWTExpired) -> JSONResponse:
  return JSONResponse(Response(status=Status.Failed,
                               msg=error_msg(exc).details_message),
                      status_code=401)


def generate_auth_key():
  kid = uuid.uuid4().hex
  pvk = jwk.JWK.generate(kty=os.environ.get('JWK_KTY'),
                         size=int(os.environ.get('JWK_SIZE')),
                         kid=kid)
  pbk = pvk.export_public()
  return AuthKeys(kid=kid, pvk=pvk, pbk=pbk)


def update_auth_key(key: AuthKeys):
  exp_time = (
      datetime.utcnow() +
      timedelta(days=int(os.environ.get('AUTH_EXP_DAYS', 7)))).timestamp()
  INPUT_OPTIONS.redis.hset('PV_KEYS', key.kid,
                           PrivateKey(pvk=key.pvk, exp=exp_time).json())
  INPUT_OPTIONS.redis.hset('PB_KEYS', key.kid,
                           PublicKey(pbk=key.pbk, exp=exp_time).json())


@app.on_event('startup')
async def startup_event():
  global INPUT_OPTIONS
  rdb = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                    port=int(os.environ.get('REDIS_PORT', 6379)),
                    db=int(os.environ.get('REDIS_DATABASE', 0)))
  if INPUT_OPTIONS is None:
    INPUT_OPTIONS = Namespace(redis=rdb)
  key = generate_auth_key()
  update_auth_key(key)
  INPUT_OPTIONS.kid = key.kid


@app.on_event('shutdown')
def shutdown_event():
  pass


# API
# ---------------------------------------------------
# GET /
# ---------------------------------------------------
@app.get('/')
async def index():
  return Response(status=Status.Success)


# ---------------------------------------------------
# GET /test
# ---------------------------------------------------
@app.get('/test')
async def test():
  return Response(status=Status.Success)


# ---------------------------------------------------
# GET /authentication
# ---------------------------------------------------
@app.get('/authentication')
async def authentication():
  val_time = 3
  exp_time = round(time.time()) + val_time
  jwt_header = {
      'alg': os.environ.get('JWT_ALG'),
      'enc': os.environ.get('JWT_ENC')
  }
  jwt_claims = {'exp': exp_time}
  jwt_token = jwt.JWT(header=jwt_header, claims=jwt_claims)
  pvk_str = INPUT_OPTIONS.redis.hdel('PV_KEYS', INPUT_OPTIONS.kid)
  pbk_str = INPUT_OPTIONS.redis.hdel('PB_KEYS', INPUT_OPTIONS.kid)
  pvk_obj = PrivateKey.parse_raw(pvk_str)
  pbk_obj = PublicKey.parse_raw(pbk_str)
  if datetime.utcnow().timestamp() > pvk_obj.exp:
    pvk = jwk.JWK(**pvk_obj.pvk)
    pbk = jwk.JWK(**pbk_obj.pbk)
  else:
    key = generate_auth_key()
    update_auth_key(key)
    pvk = key.pvk
    pbk = key.pbk
  jwt_token.make_encrypted_token(pvk)
  return AuthResponse(status=Status.Success,
                      token=jwt_token,
                      key=pbk,
                      exp=exp_time)


# ---------------------------------------------------
# POST /authentication
# ---------------------------------------------------
@app.post('/authentication')
async def authentication_post(req: Request):
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail='Could not validate credentials',
      headers={'WWW-Authenticate': 'Bearer'},
  )
  json_data = json.loads((await req.body()).decode())
  data = json_data.get('data')
  token_str = req.headers.get('Authorization')
  if token_str is None:
    raise credentials_exception
  pvk_str = INPUT_OPTIONS.redis.hdel('PV_KEYS', INPUT_OPTIONS.kid)
  pvk_obj = PrivateKey.parse_raw(pvk_str)
  pvk = jwk.JWK(**pvk_obj.pvk)
  token = jwt.JWT()
  token.deserialize(token_str, pvk)
  data_split = data.split('@')
  kid = data_split[0]
  if len(data_split) > 0 and not pvk_str is None:
    if datetime.utcnow() < pvk_obj.exp:
      jwetoken = jwe.JWE()
      jwetoken.deserialize(data_split[1], key=pvk)
      payload = jwetoken.payload.decode('utf-8')
      if not payload is None and payload:
        secret_infos = json.loads(payload)
        verify = (secret_infos['username'] == 'abc12345') and\
          (secret_infos['password'] == '1234567890')
        INPUT_OPTIONS['redis'].hdel('PV_KEYS', kid)
        return AuthResponse(status=Status.Success, verify=verify)
  raise credentials_exception


if __name__ == '__main__':
  import uvicorn
  uvicorn.run('main:app',
              host='0.0.0.0',
              port=3000,
              reload=True,
              log_level='debug')
