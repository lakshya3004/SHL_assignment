from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# Placeholder for API key authentication if needed in the future
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def validate_api_key(api_key: str = Security(api_key_header)):
    """
    Validate the incoming API key. 
    Currently a placeholder for future security implementation.
    """
    # TODO: Implement actual API key validation logic
    if settings.DEBUG:
        return True
        
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key missing"
        )
    
    # Example logic: if api_key != settings.SECRET_KEY: raise ...
    return api_key
