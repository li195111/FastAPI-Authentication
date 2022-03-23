import json
import uuid
from datetime import datetime, timedelta
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jwcrypto import jwk, jwe
import redis
from utils import error_msg, utc_now

app = FastAPI()
origins = [
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rdb = redis.Redis(host='localhost',port=6379,db=0)

jwt_valid_seconds = 3
expiry_time = round(time.time()) + jwt_valid_seconds

@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({'status':'failed','time':utc_now(),'msg':error_msg(exc).details_message}, status_code=404)

@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
def shutdown_event():
    pass

# API
# ---------------------------------------------------
# GET /
# ---------------------------------------------------
@app.get('/')
async def index(req:Request):
    return {'status':'success','time':datetime.utcnow()}

@app.get('/test')
async def test(req:Request):
    return {'status':'success','time':datetime.utcnow()}

@app.get('/authentication')
async def authentication(req:Request):
    try:
        kid = uuid.uuid4().hex
        private_key = jwk.JWK.generate(kty='RSA',size=2048, kid=kid)
        public_key = private_key.export_public()
        expiry_time = (datetime.utcnow() + timedelta(seconds=3)).timestamp()
        rdb.hset('KEY_PAIR', kid, json.dumps({'key':private_key,'exp':expiry_time}))
        return {'status':'success','time':datetime.utcnow(),'publicKey':public_key,'expiry_time':expiry_time,"kid":kid} 
    except Exception as e:
        return {'status':'failed','time':datetime.utcnow(),'msg':error_msg(e)}

@app.post('/authentication')
async def authentication(req:Request):
    try:
        data = json.loads((await req.body()).decode())
        loginInfo = data.get('data')
        if loginInfo:
            datas = loginInfo.split('@')
            kid = datas[0]
            KEY_STR = rdb.hget('KEY_PAIR',kid)
            if len(datas) > 0 and not KEY_STR is None:
                KEY = json.loads(KEY_STR)
                if datetime.fromtimestamp(KEY['exp']) > datetime.utcnow():
                    jwetoken = jwe.JWE()
                    jwetoken.deserialize(datas[1], key=jwk.JWK(**KEY['key']))
                    payload = jwetoken.payload.decode('utf-8')
                    if not payload is None and payload:
                        secret_infos = json.loads(payload)
                        verify = (secret_infos['username'] == 'abc12345') and (secret_infos['password'] == '1234567890')
                        rdb.hdel('KEY_PAIR',kid)
                        return {'status':'success','time':datetime.utcnow(),'verify':verify}
                    return {'status':'failed','time':datetime.utcnow(),'verify':False, 'reason':'no payload.'} 
                return {'status':'failed','time':datetime.utcnow(),'verify':False, 'reason':'Token Expired.'} 
        return {'status':'failed','time':datetime.utcnow(),'verify':False, 'reason':'no data received.'} 
    except Exception as e:
        return {'status':'failed','time':datetime.utcnow(),'msg':error_msg(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=True, log_level='debug')

