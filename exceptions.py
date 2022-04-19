'''
HTTP Exceptions Handlers
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse

import jwcrypto.jwt
import jwcrypto.jwe
import jose.jwt


class InactiveUser(HTTPException):

  def __init__(self) -> None:
    status_code = 400
    detail = 'Inactive User'
    super().__init__(status_code, detail)


class InvalidUser(HTTPException):

  def __init__(self) -> None:
    status_code = 401
    detail = 'Incorrect username or password'
    headers = {'WWW-Authenticate': 'Bearer'}
    super().__init__(status_code, detail, headers)


class UserNotFound(HTTPException):

  def __init__(self) -> None:
    status_code = 404
    detail = 'User Not Found'
    super().__init__(status_code, detail)


class EmailAlreadyUsed(HTTPException):

  def __init__(self) -> None:
    status_code = 409
    detail = 'email already be used'
    super().__init__(status_code, detail)


class EmailAlreadyActive(HTTPException):

  def __init__(self) -> None:
    status_code = 409
    detail = 'email already active'
    super().__init__(status_code, detail)


class UsernameAlreadyUsed(HTTPException):

  def __init__(self) -> None:
    status_code = 409
    detail = 'username already be used'
    super().__init__(status_code, detail)


class InvalidToken(HTTPException):

  def __init__(self) -> None:
    status_code = 400
    detail = 'X-Token Header Invalid'
    super().__init__(status_code, detail)


class TokenExpired(HTTPException):

  def __init__(self) -> None:
    status_code = 401
    detail = 'Token Expired'
    headers = {'WWW-Authenticate': 'Bearer'}
    super().__init__(status_code, detail, headers)


class NotAuthenticated(HTTPException):

  def __init__(self) -> None:
    status_code = 401
    detail = 'Not authenticated'
    headers = {'WWW-Authenticate': 'Bearer'}
    super().__init__(status_code, detail, headers)


class InvalidCredentials(HTTPException):

  def __init__(self) -> None:
    status_code = 401
    detail = 'Could not validate credentials'
    headers = {'WWW-Authenticate': 'Bearer'}
    super().__init__(status_code, detail, headers)


class PermissionDenied(HTTPException):

  def __init__(self) -> None:
    status_code = 401
    detail = 'Permission denied'
    super().__init__(status_code, detail)


def setup_exceptions(app: FastAPI):

  @app.exception_handler(jwcrypto.jwt.JWTExpired)
  @app.exception_handler(PermissionDenied)
  async def jwt_expired_exception_handler(
      request: Request, exc: jwcrypto.jwt.JWTExpired | PermissionDenied):
    return JSONResponse(status_code=401,
                        content={'details': 'Permission denied'})

  @app.exception_handler(jose.jwt.JWTError)
  @app.exception_handler(InvalidCredentials)
  async def jwt_invalid_exception_handler(
      request: Request, exc: jose.jwt.JWTError | InvalidCredentials):
    return JSONResponse(status_code=401,
                        content={'details': 'Could not validate credentials'},
                        headers={'WWW-Authenticate': 'Bearer'})

  @app.exception_handler(jwcrypto.jwe.InvalidJWEData)
  async def jwe_key_exception_handler(request: Request,
                                      exc: jwcrypto.jwe.InvalidJWEData):
    return JSONResponse(status_code=401,
                        content={'details': 'Invalid Credentials'},
                        headers={'WWW-Authenticate': 'Bearer'})

  @app.exception_handler(InvalidToken)
  async def jwt_header_invalid_exception_handler(request: Request,
                                                 exc: InvalidToken):
    return JSONResponse(status_code=401, content={'details': 'Invalid Token'})

  @app.exception_handler(NotAuthenticated)
  async def jwt_authorize_failed_exception_handler(request: Request,
                                                   exc: NotAuthenticated):
    return JSONResponse(status_code=401,
                        content={'details': 'Not authenticated'},
                        headers={'WWW-Authenticate': 'Bearer'})

  @app.exception_handler(InactiveUser)
  async def user_inactive_exception_handler(request: Request,
                                            exc: InactiveUser):
    return JSONResponse(status_code=400, content={'details': 'Inactive User'})

  @app.exception_handler(InvalidUser)
  async def user_exception_handler(request: Request, exc: InvalidUser):
    return JSONResponse(status_code=401,
                        content={'details': 'Incorrect username or password'},
                        headers={'WWW-Authenticate': 'Bearer'})

  @app.exception_handler(UserNotFound)
  async def user_notfound_exception_handler(request: Request,
                                            exc: UserNotFound):
    return JSONResponse(status_code=404, content={'details': 'User Not Found'})

  @app.exception_handler(Exception)
  async def http_exception_handler(request: Request,
                                   exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={'details': 'Not Found'})
