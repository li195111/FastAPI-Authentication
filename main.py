'''
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
OAuth2 FastAPI Implements
'''
import os
from datetime import timedelta

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import exceptions as exce
import dependencies
import database
import options
import routers
import models

origins = [
    'http://localhost:3001',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
    'http://192.168.1.101:8001',
    'http://192.168.1.100:8001',
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(routers.users.router)
exce.setup_exceptions(app)


@app.on_event('startup')
async def startup_event(db: Session = database.get_db(),
                        opts=options.get_opts()):
  opts.jwt_header = {
      'alg': os.environ.get('JWT_ALG'),
      'enc': os.environ.get('JWT_ENC')
  }
  opts.jwk_kty = os.environ.get('JWK_KTY')
  opts.jwk_size = int(os.environ.get('JWK_SIZE'))
  opts.jwt_exp_mins = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
  opts.jwt_exp_days = int(os.environ.get('AUTH_EXP_DAYS', 7))
  opts.jwt_access_alg = os.environ.get('ALGORITHM')
  opts.jwt_access_key = os.environ.get('SECRET_KEY')
  opts.email_secret = os.environ.get('EMAIL_SECRET')
  assert opts.email_secret, ValueError('Email Secret must given')
  opts.debug = os.environ.get('DEBUG', True)
  if opts.debug:
    opts.front_host = os.environ.get('DEV_FRONT_HOST', 'localhost')
    opts.front_port = os.environ.get('DEV_FRONT_PORT', 8001)
  else:
    opts.front_host = os.environ.get('DEP_FRONT_HOST')
    opts.front_port = os.environ.get('DEP_FRONT_PORT', 8001)
  assert opts.front_host, ValueError('Host must given')
  assert opts.front_port, ValueError('Port must given')

  opts.front_dns = os.environ.get('FRONT_DNS', '')
  database.rdb_clear_keys()
  models.generate_fake_user(db)
  keys = dependencies.generate_auth_key(opts,
                                        timedelta(days=opts.jwt_exp_days))
  dependencies.update_auth_key(keys)
  opts.kid = keys.kid


@app.get('/')
async def index():
  return {'Message': 'Hello'}


@app.get('/verify')
async def verify(auth: models.Auth = Depends(dependencies.verify)):
  return auth


@app.post('/authorize')
async def authorize(token: str = Depends(dependencies.authorize)):
  return {'token': token}


@app.post('/token', response_model=models.AccessToken)
async def login_for_access_token(opts=Depends(options.get_opts),
                                 token: str = Depends(
                                     dependencies.oauth2_scheme),
                                 db: Session = Depends(database.get_db)):
  form_with_key = dependencies.model_parse(opts, models.OAuth2UserFormWithKey,
                                           token)
  user = dependencies.authenticate_user_form(form_with_key.form, db)
  claims = {'sub': user.email, 'key': form_with_key.key}
  access_exp = timedelta(minutes=opts.jwt_exp_mins)
  for access_token in dependencies.create_access_token(opts,
                                                       claims=claims,
                                                       exp_delta=access_exp):
    return {'access_token': access_token, 'token_type': 'bearer'}


if __name__ == '__main__':
  import uvicorn
  uvicorn.run('main:app',
              host='0.0.0.0',
              port=3001,
              reload=True,
              log_level='debug',
              log_config='log_conf.yaml')
