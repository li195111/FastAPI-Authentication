# FastAPI-Authentication
FastAPI RESTful Authentication API use JWT(Json Web Token) Implements

# Requirements
- Python 3 (Back-End)
- Redis
    - [Windows .msi install Version](https://github.com/MicrosoftArchive/redis)
    - Mac OS `brew install redis`
    - Linux - Following Command

        ```
        sudo apt update
        sudo apt install redis-server
        ```

- NodeJS (Front-End)
# HOW TO

Following command will run redis-server automatically. 

1. make sure your environment already installed redis.
2. to front-end folder.
```
cd auth-front-end
```
3. install packages.
```
npm i
```
4. back to root folder.
```
cd ..
```
5. Run the following execute command.
```
python run.py
```
6. and open browser to http://localhost:3001
