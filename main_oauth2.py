from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from model import User, Response, UserInDB, Token, TokenData

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "81f5abb8f0569b860a14ecab70dbb66b9477b4a42a68a90c4c43212bea5f9597"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_user_db = {
    'johndoe': {
        'username': 'johndoe',
        'full_name': 'John Doe',
        'email': 'johndoe@example.com',
        'hashed_password': 'fakehashedsecret',
        'disable': False
    },
    'alice': {
        'username': 'alice',
        'full_name': 'Alice Wonderson',
        'email': 'alice@example.com',
        'hashed_password': 'fakehashedsecret2',
        'disable': True
    }
}

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()

def verify_password(plain_password, hashed_password):
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
  return pwd_context.hash(password)

def fake_hash_password(password: str):
  return 'fakehashed' + password

def get_user(db, username: str):
  if username in db:
    user_dict = db[username]
    return UserInDB(**user_dict)

def authenticate_user(fake_db, username:str, password:str):
  user = get_user(fake_db, username)
  if not user:
    return False
  if not verify_password(password, user.hashed_password):
    return False
  return user

def create_access_token(data:dict, exp_delta:timedelta=timedelta(minutes=15)):
  to_encode = data.copy()
  exp = datetime.utcnow() + exp_delta
  to_encode.update({'exp':exp})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

def fake_docode_token(token):
  user = get_user(fake_user_db, token)
  return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
  user = fake_docode_token(token)
  if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
  return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)):
  if current_user.disable:
    raise HTTPException(status_code=400, detail='Inactive User')
  return current_user


@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  user_dict = fake_user_db.get(form_data.username)
  if not user_dict:
    raise HTTPException(status_code=400,
                        detail='Incorrect username or password')
  user = UserInDB(**user_dict)
  hashed_password = fake_hash_password(form_data.password)
  if not hashed_password == user.hashed_password:
    raise HTTPException(status_code=400,
                        detail='Incorrect username or password')
  return {'access_token': user.username, 'token_type': 'bearer'}


@app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_active_user)):
  return current_user


@app.get('/items/')
async def read_items(token: str = Depends(oauth2_scheme)):
  return {'token': token}


if __name__ == '__main__':
  import uvicorn
  uvicorn.run('main_oauth2:app',
              host='0.0.0.0',
              port=3001,
              reload=True,
              log_level='debug')
