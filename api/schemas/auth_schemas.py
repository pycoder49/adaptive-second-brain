from pydantic import BaseModel

"""
Schemas for auth related stuff
"""

class TokenResponse(BaseModel):
    access_token: str
    token_type: str