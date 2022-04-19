'''
Models Modules
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import os
import json
from .base import *
from .enums import *
from .items import *
from .key import *
from .response import *
from .sql import *
from .token import *
from .users import *

import crud
import exceptions as exce

database.SQLBase.metadata.create_all(bind=database.ENGINE)


def User2SQLUser(user: User) -> SQLUser:
  return SQLUser(id=user.id,
                 uid=user.uid,
                 full_name=user.full_name,
                 permission=user.permission,
                 email=user.sub,
                 password=user.password,
                 salt=user.salt,
                 items=user.items,
                 create=user.create,
                 is_active=user.is_active)


def User2UserInfo(user: User) -> UserInfo:
  return UserInfo(full_name=user.full_name,
                  sub=user.sub,
                  uid=user.uid,
                  items=user.items)


def SQLUser2User(user: SQLUser) -> User:
  return User(id=user.id,
              uid=user.uid,
              full_name=user.full_name,
              permission=user.permission,
              sub=user.email,
              password=user.password,
              salt=user.salt,
              items=user.items,
              create=user.create,
              is_active=user.is_active)


def UserCreate2User(user: UserCreate) -> User:
  return User(full_name=user.full_name,
              sub=user.sub,
              password=user.password,
              salt=user.salt)


def SQLUser2UserInfo(user: SQLUser) -> UserInfo:
  return UserInfo(
      full_name=user.full_name,
      sub=user.email,
      uid=user.uid,
      items=user.items,
  )


def generate_fake_user(db_gen: list[database.Session],
                       file_path: str = 'fixtures.json'):
  if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as fp:
      fake_users = json.load(fp)
    for db in db_gen:
      for fake_user in fake_users:
        fake_user = UserCreate(**fake_user)
        fake_user = UserCreate2User(fake_user)
        try:
          crud.create_user_if_not_exists(db, fake_user)
        except exce.EmailAlreadyUsed:
          pass
