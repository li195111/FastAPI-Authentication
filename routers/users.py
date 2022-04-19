'''
Users Router Module
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import exceptions as exce
import email_validation
import dependencies
import database
import options
import models
import crud

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {
        'description': 'Not Found'
    }},
)


@router.get('/all',
            response_model=list[models.UserInfo],
            dependencies=[Depends(dependencies.get_super_manager)])
async def read_users(skip: int = 0,
                     limit: int = 100,
                     db: Session = Depends(database.get_db)):
  db_users = crud.get_users(db, skip, limit)
  users = [models.SQLUser2UserInfo(db_user) for db_user in db_users]
  return users


@router.get('/verify', response_model=models.Auth)
async def verify(auth: models.Auth = Depends(dependencies.verify)):
  return auth


@router.post('/', response_model=models.Token)
def create_user(opts=Depends(options.get_opts),
                token: str = Depends(dependencies.oauth2_scheme),
                db: Session = Depends(database.get_db)):
  user_data = dependencies.model_parse(opts, models.UserCreateWithKey, token)
  user = models.UserCreate2User(user_data.user_create)
  db_user = crud.create_user_if_not_exists(db, user)
  user_info = dependencies.jose_token_encode(
      opts, json.loads(models.SQLUser2UserInfo(db_user).json()), user_data.key)
  detail = email_validation.send_validation(opts, db_user, user_data.key)
  return models.Token(token=user_info, detail=detail)


@router.get('/revalidation', response_model=models.Token)
def resend_validation(opts=Depends(options.get_opts),
                      token: str = Depends(dependencies.oauth2_scheme),
                      db: Session = Depends(database.get_db)):
  user_data = dependencies.model_parse(opts, models.ValidationUser, token)
  db_user = dependencies.get_user_by_sub(db, user_data.sub)
  if not db_user.is_active:
    user_info = dependencies.jose_token_encode(
        opts, json.loads(models.SQLUser2UserInfo(db_user).json()),
        user_data.key)
    detail = email_validation.send_validation(opts, db_user, user_data.key)
    return models.Token(token=user_info, detail=detail)
  raise exce.EmailAlreadyActive()


@router.post('/validation', response_model=models.Token)
async def validation_email(opts=Depends(options.get_opts),
                           token: str = Depends(dependencies.oauth2_scheme),
                           db: Session = Depends(database.get_db)):
  user_data = dependencies.model_parse(opts, models.ValidationUser, token)
  db_user = dependencies.get_user_by_sub(db, user_data.sub)
  if not db_user.is_active:
    db_user.is_active = True
    crud.update_user_active(db, db_user)
    user_info = dependencies.jose_token_encode(
        opts, json.loads(models.SQLUser2UserInfo(db_user).json()),
        user_data.key)
    return models.Token(token=user_info)
  raise exce.EmailAlreadyActive()


@router.get('/{uid}',
            response_model=models.Token,
            dependencies=[Depends(dependencies.get_super_manager)])
async def read_user(opts=Depends(options.get_opts),
                    user_with_key: models.UserWithKey = Depends(
                        dependencies.get_current_active_user)):
  user_info = dependencies.jose_token_encode(
      opts, json.loads(models.User2UserInfo(user_with_key.user).json()),
      user_with_key.key)
  return models.Token(token=user_info)


@router.put('/{uid}',
            dependencies=[Depends(dependencies.get_super_manager)],
            tags=['custom'],
            response_model=models.Token,
            responses={403: {
                'description': 'Operation forbidden'
            }})
async def update_user(opts=Depends(options.get_opts),
                      user_with_key: models.UserWithKey = Depends(
                          dependencies.get_current_active_user),
                      db: Session = Depends(database.get_db)):
  crud.update_user(db, user_with_key.user)
  user_info = dependencies.jose_token_encode(
      opts, json.loads(models.User2UserInfo(user_with_key.user).json()),
      user_with_key.key)
  return models.Token(token=user_info)


# @router.post('/{user_id}/items/', response_model=models.Item)
# def create_item_for_user(user_id: int,
#                          item: models.ItemCreate,
#                          db: Session = Depends(database.get_db)):
#   return crud.create_user_item(db, item, user_id)


@router.get('/me/', response_model=models.Token)
async def read_users_me(opts=Depends(options.get_opts),
                        user_with_key: models.UserWithKey = Depends(
                            dependencies.get_current_active_user)):
  claims = json.loads(models.User2UserInfo(user_with_key.user).json())
  user_info = dependencies.jose_token_encode(opts, claims, user_with_key.key)
  return models.Token(token=user_info)


@router.get('/me/items/', response_model=models.Token)
async def read_own_items(opts=Depends(options.get_opts),
                         user_with_key: models.UserWithKey = Depends(
                             dependencies.get_current_active_user)):
  claims = models.User2UserInfo(user_with_key.user).items
  user_info = dependencies.jose_token_encode(opts, claims, user_with_key.key)
  return models.Token(token=user_info)
