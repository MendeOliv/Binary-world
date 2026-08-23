from fastapi import Header, HTTPException, Security, status
from app.config import settings

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Dependency to verify the API key provided in the X-API-Key header.
    """
    if x_api_key != settings.HERMES_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key
