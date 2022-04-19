'''
Items Router Module
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import database
import models
import crud

router = APIRouter(
    prefix='/items',
    tags=['items'],
    dependencies=[],
    responses={404: {
        'description': 'Not Found'
    }},
)

fake_items_db = {'plumbus': {'name': 'Plumbus'}, 'gun': {'name': 'Portal Gun'}}


@router.get('/')
async def read_items(skip: int = 0,
                     limit: int = 100,
                     db: Session = Depends(database.get_db)):
  items = crud.get_items(db, skip, limit)
  return items


@router.get('/{item_id}')
async def read_item(item_id: str, db: Session = Depends(database.get_db)):
  item = crud.get_item(db, item_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Item Not Found')
  return item


@router.put('/{item_id}',
            tags=['custom'],
            responses={403: {
                'description': 'Operation forbidden'
            }})
async def update_item(item: models.Item,
                      db: Session = Depends(database.get_db)):
  if item.title != 'plumbus' or item.title != 'The Great Plumbus':
    raise HTTPException(status_code=403,
                        detail='You Can Only Update the item: plumbus')
  db_item = crud.update_item(db, item)
  if db_item is None:
    raise HTTPException(status_code=404, detail='Item Not Found')
  return db_item
