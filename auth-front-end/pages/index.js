import Head from 'next/head'
import Image from 'next/image'
import Script from 'next/script'
import styles from '../styles/Home.module.css'
import Btn from './components/button'
import TextArea from './components/textarea'
import InputBlock from './components/inputBlock'
import { useRef } from 'react'
import { loginUser, userInfos } from './api/auth'

export default function Home() {
    const nameForm = useRef(null);
    async function handleAuth(e){
        e.preventDefault();
        const form = nameForm.current;
        // Process Login Infos
        loginUser(form);
    }
    async function handleDetails(e){
        e.preventDefault();
        const form = nameForm.current;
        userInfos(form);
    }
    return (
        <div className={styles.container}>
            <Head>
                <title>FastAPI Authentication Front-End</title>
                <meta name="description" content="FastAPI Authentication Front-End" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <main className={`${styles.main}`}>
                <h1 className=''>FastAPI Authentication</h1>
                <form className={`${styles.card} v-flex v-ai-flex-center p-lr-100`} ref={nameForm}>
                    <InputBlock id='username' type='text' name='username' text='Username' defaultValue='abc12345'/>
                    <InputBlock id='password' type='password' name='password' text='Password' defaultValue='1234567890'/>
                    <Btn id='auth' text='Authentication' onclick={handleAuth}/>
                    <TextArea id='token-area' name='token-area' text='Token'/>
                    <Btn id='details' text='Check Details' onclick={handleDetails} />
                    <TextArea id='result-area' name='result-area' text='Result'/>
                </form>
            </main>

            <footer className={styles.footer}>
                QChoice Tech, LTD.
            </footer>
        </div>
    )
}
