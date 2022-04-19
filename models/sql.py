'''
SQL Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

import database


# SQL Models
class SQLUser(database.SQLBase):
  '''SQL User Model'''
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  uid = Column(String, nullable=False, unique=True, index=True)
  email = Column(String, nullable=False, unique=True, index=True)
  password = Column(
      String,
      nullable=False,
  )
  salt = Column(String)
  iter = Column(Integer)
  keylen = Column(Integer)
  digest = Column(String)
  full_name = Column(String)
  permission = Column(Integer, default=1, nullable=False)
  create = Column(DateTime, index=True, nullable=False)
  is_active = Column(Boolean, default=False)
  items = relationship('SQLItem', back_populates='owner')


class SQLItem(database.SQLBase):
  __tablename__ = 'items'
  id = Column(Integer, primary_key=True, index=True)
  uid = Column(String, unique=True, index=True)
  title = Column(String, index=True)
  description = Column(String)
  owner_id = Column(Integer, ForeignKey('users.id'))
  owner = relationship('SQLUser', back_populates='items')
