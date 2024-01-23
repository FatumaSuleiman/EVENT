
from firebase_admin import credentials,auth
from firebase_admin import firestore
from starlette.responses import JSONResponse,Response
from fastapi import HTTPException
from fastapi import Security,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from datetime import datetime,timedelta
import jwt
security=HTTPBearer()
from starlette.requests import Request
import logging

secret = "secret"
def find_user(self,email):
    user=auth.get_user_by_email(email)
    if not user is None:
        return JSONResponse(content=f"user for the email:{user}".format(email))

def encode_token(user_id):
    payload = {
        'exp': datetime.now() + timedelta(hours=8),
        'iat': datetime.now(),
        'sub': user_id,
        'premiumAccount': True,
    }
    return jwt.encode(payload, secret, algorithm='HS256')
def decode_token( token):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Expired signature')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')
    
def get_current_user(request: Request,cred:HTTPAuthorizationCredentials=Depends(HTTPBearer(auto_error=False))):
    """Get the user details from Firebase, based on TokenID in the request
    :param request: The HTTP request
    """
    id_token = request.headers.get('Authorization')
    if not id_token:
        raise HTTPException(status_code=400, detail='TokenID must be provided')

    try:
        claims = auth.verify_id_token(id_token.split(" ")[1])
        return claims
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=401, detail='Unauthorized')


""""
def get_current_user(res:Response,cred:HTTPAuthorizationCredentials=Depends(HTTPBearer(auto_error=False))):
    if cred is None:
        raise HTTPException(
            status_code=401,
            detail="Bearer authentication is needed",
            headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
            
        )
    try:
        user = auth.get_user(uid)
    except Exception as err:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication from Firebase. {err}",
              headers={'WWW-Authenticate': 'Bearer error="invalid_token"'},
        )
    res.headers['WWW-Authenticate'] = 'Bearer realm="auth_required"'
    return user.uid
***/

def get_current_users(cred: HTTPAuthorizationCredentials =Depends(HTTPBearer(auto_error=False))):
        if cred is None:
            raise HTTPException(
            status_code=401,
            detail="Bearer authentication is needed",
            
        )
       
        email =decode_token(cred.credentials)
        if email is None:
            raise HTTPException(
            status_code=401,
            detail="Bearer authentication is needed",
            
        )
        user =auth.get_user_by_email(email=email)
        if user is None:
            raise HTTPException(detail='invalid email')
        return user
"""