from fastapi import Header, HTTPException, status, Query
from jwt_utils import verify_token

async def jwt_auth(
   
    token: str = Query(None)  # check query param
):
    token_to_check = None

    # first check Authorization header
    if token:
        token_to_check = token

   
    if not token_to_check:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    payload = verify_token(token_to_check)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload
