from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.utils import decode_token


class AccessToken(HTTPBearer):
    
    def __iniit__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not self.valid_token(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        if token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Provide a valid access token")
        return token_data
    
    def valid_token(self, token: str):
        token_data = decode_token(token)
        return True if token_data is not None else False