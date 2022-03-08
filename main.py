import json
import hashlib
import uuid
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from jwcrypto import jwt, jwa, jwk, jws, jwe

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

KEY_PAIR = {}

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
        KEY_PAIR[kid] = private_key
        return {'status':'success','time':datetime.utcnow(),'publicKey':public_key,"kid":kid} 
    except:
        return {'status':'failed','time':datetime.utcnow()}

@app.post('/authentication')
async def authentication(req:Request):
    try:
        
        data = json.loads((await req.body()).decode())
        loginInfo = data.get('data')
        if loginInfo:
            datas = loginInfo.split('@')
            kid = datas[0]
            enc = datas[1]
            jwetoken = jwe.JWE()
            jwetoken.deserialize(enc, key=KEY_PAIR[kid])
            payload = jwetoken.payload.decode('utf-8')
            if not payload is None and payload:
                secret_infos = json.loads(payload)
                verify = (secret_infos['username'] == 'abc12345') and (secret_infos['password'] == '1234567890')
                return {'status':'success','time':datetime.utcnow(),'verify':verify}
        return {'status':'failed','time':datetime.utcnow(),'verify':False} 
    except:
        return {'status':'failed','time':datetime.utcnow(),'verify':False} 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=True, log_level='debug')

