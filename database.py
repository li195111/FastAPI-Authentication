'''
Database Module
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import redis

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite://:memory:')
ENGINE = create_engine(DATABASE_URL, echo=False, future=True)
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
SQLBase = declarative_base()


def get_db():
  db = SESSION_LOCAL()
  try:
    yield db
  finally:
    db.close()


def rdb_init():
  rdb = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                    port=int(os.environ.get('REDIS_PORT', 6379)),
                    db=int(os.environ.get('REDIS_DATABASE', 0)))
  return rdb


def rdb_clear_keys():
  rdb = rdb_init()
  # Clear old data
  rnms = ['PV_KEYS', 'PB_KEYS']
  for rnm in rnms:
    for k in rdb.hgetall(rnm):
      rdb.hdel(rnm, k)
  rdb.close()


def get_rdb():
  rdb = rdb_init()
  try:
    yield rdb_init()
  finally:
    rdb.close()
