'''
SQL Operations
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from sqlalchemy.orm import Session

import models
import exceptions as exce


def get_user_query_by_email(db: Session, email: str):
  return db.query(models.SQLUser).filter(models.SQLUser.email == email)


def get_user_query_by_uid(db: Session, uid: str):
  return db.query(models.SQLUser).filter(models.SQLUser.uid == uid)


def get_user_by_email(db: Session, email: str) -> models.SQLUser | None:
  return get_user_query_by_email(db, email).first()


def get_user_by_uid(db: Session, uid: str) -> models.SQLUser | None:
  return get_user_query_by_uid(db, uid).first()


def get_users(db: Session,
              skip: int = 0,
              limit: int = 100) -> list[models.UserInfo]:
  return db.query(models.SQLUser).offset(skip).limit(limit).all()


# User Update
def update_user_column(db: Session, user: models.SQLUser, column_values: dict):
  q = get_user_query_by_email(db, user.email)
  q.update(column_values)
  db.commit()


def update_user_active(db: Session, user: models.SQLUser):
  update_user_column(db, user, {models.SQLUser.is_active: user.is_active})


def update_user_password(db: Session, user: models.SQLUser):
  update_user_column(db, user, {models.SQLUser.password: user.password})


def update_user_full_name(db: Session, user: models.SQLUser):
  update_user_column(db, user, {models.SQLUser.full_name: user.full_name})


def update_user_email(db: Session, user: models.SQLUser):
  update_user_column(db, user, {models.SQLUser.email: user.email})


def update_user_items(db: Session, user: models.SQLUser):
  update_user_column(db, user, {models.SQLUser.items: user.items})


# User Create
def create_user(db: Session, user: models.SQLUser) -> models.SQLUser:
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


def create_user_if_not_exists(db: Session,
                              user: models.User) -> models.SQLUser:
  user = get_user_by_email(db, user.sub)
  if user is None:
    user = models.User2SQLUser(user)
    return create_user(db, user)
  raise exce.EmailAlreadyUsed()


# Item
# def get_items(db: Session,
#               skip: int = 0,
#               limit: int = 100) -> list[models.SQLItem] | None:
#   return db.query(models.SQLItem).offset(skip).limit(limit).all()

# def get_item(db: Session, item_id: int) -> models.SQLItem | None:
#   return db.query(models.SQLItem).filter(models.SQLItem.id == item_id).first()

# def update_item(db: Session, item: models.Item) -> models.SQLItem:
#   db.query(models.SQLItem).filter(models.SQLItem.id == item.id).update({
#       models.SQLItem.title:
#       item.title,
#       models.SQLItem.description:
#       item.description,
#       models.SQLItem.owner_id:
#       item.owner_id
#   })
#   db.commit()
#   return get_item(db, item.id)

# def create_user_item(db: Session, item: models.ItemCreate,
#                      user_id: int) -> models.SQLItem:
#   db_item = models.SQLItem(**item.dict(), owner_id=user_id)
#   db.add(db_item)
#   db.commit()
#   db.refresh(db_item)
#   return db_item
