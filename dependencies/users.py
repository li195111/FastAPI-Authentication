'''
User Dependencies
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import os
import json

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from . import token as tkn
import exceptions as exce
import database
import options
import crypto
import models
import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def model_parse(opts, model: models.IBase, token: str):
  user = None
  for claims in tkn.token_decode(opts, token):
    if isinstance(claims, str):
      claims = json.loads(claims)
    user = model.parse_obj(claims)
  if user is None:
    raise exce.PermissionDenied()
  return user


def get_user_by_sub(db: Session, sub: str):
  user = crud.get_user_by_email(db, sub)
  if user is None:
    raise exce.UserNotFound()
  return user


def verify(opts=Depends(options.get_opts)):
  for auth in tkn.get_auth(opts):
    yield auth


def authorize(token=Depends(oauth2_scheme),
              opts=Depends(options.get_opts),
              db: Session = Depends(database.get_db)):
  user = None
  user_data = model_parse(opts, models.Verify, token)
  user = get_user_by_sub(db, user_data.sub)
  user = models.SQLUser2User(user)
  for auth in tkn.get_auth(opts):
    token = tkn.jose_token_encode(opts, {
        'sub': user.sub,
        'salt': user.salt,
        'key': auth.key
    }, user_data.key)
    yield token


def authenticate_user_form(form_data: models.OAuth2UserForm,
                           db: Session) -> models.SQLUser:
  user = get_user_by_sub(db, form_data.sub)
  if not user:
    return None
  if not crypto.verify_password(form_data.password, user.password):
    return None
  if user is None:
    raise exce.InvalidUser()
  return user


def get_current_user(opts=Depends(options.get_opts),
                     token: str = Depends(oauth2_scheme),
                     db: Session = Depends(
                         database.get_db)) -> models.UserWithKey:
  user_data = model_parse(opts, models.ValidationUser, token)
  sql_user = get_user_by_sub(db, user_data.sub)
  return models.UserWithKey(user=models.SQLUser2User(sql_user),
                            key=user_data.key)


def get_current_active_user(user_with_key: models.UserWithKey = Depends(
    get_current_user)) -> models.UserWithKey:
  if not user_with_key.user.is_active:
    raise exce.InactiveUser()
  return user_with_key


def get_super_manager(x_token: str = Header(...)):
  super_token = os.environ.get('X_SUPER_TOKEN')
  if super_token is None or\
    x_token != super_token or\
    not tkn.verify_token_manager(super_token):
    raise exce.PermissionDenied()
