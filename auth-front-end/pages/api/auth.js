import axios from 'axios';
import * as jose from 'jose';

const url = 'http://localhost:3000/authentication';
const alg = 'RSA-OAEP-256';
const enc = 'A256CBC-HS512';

export const loginUser = async (form)=>{
    await axios.get(url,null)
    .then(async (res) => {
        const publicKey = await jose.importJWK(JSON.parse(res.data['publicKey']), alg);
        const jwe = await new jose.CompactEncrypt(
            new TextEncoder().encode(
                JSON.stringify({'username':form['username'].value,'password':form['password'].value})
            )
        )
        .setProtectedHeader({ alg: alg, enc: enc })
        .encrypt(publicKey);
        form['token-area'].value = res.data['kid']+"@"+jwe;
    });
}

export const userInfos = async (form) => {
    const jwe = form['token-area'].value;
    await axios.post(url,{data:jwe})
    .then(res => {
        form['result-area'].value = JSON.stringify(res.data);
    });
}