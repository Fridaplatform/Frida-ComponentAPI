from typing import Optional
from pydantic import BaseModel, Field


class ComponentRequest(BaseModel):
    prompt: str
    replaces: Optional[str] = ""


class GitHubRepository(BaseModel):
    repo_name: str = Field(..., description="The name of the repository.")
    token: str = Field(..., description="The token to access the repository.")
    branch: str = Field("main", description="The branch of the repository.")

    class Config:
        json_schema_extra = {
            "example": {
                "repo_name": "Your GitHub repository name",
                "token": "Your GitHub access token",
                "branch": "Your branch name",
            }
        }


class ChatSearchRequest(BaseModel):
    repo_name: str = Field(..., description="The name of the repository.")
    repo_branch: str = Field(..., description="The name of the branch.")
    prompt: str = Field(..., description="The message sent by the user.")
