from typing import Optional
from pydantic import BaseModel, Field


class ComponentRequest(BaseModel):
    prompt: str
    replaces: Optional[str] = ""

class CodeRequest(BaseModel):

    '''
    #CodeRequest:
    Data model for representing a request for code generation.

    ##Attributes:
    - `language (str): Programming language for which the code needs to be generated.
    - `snippet (str): Code snippet or template to be used for code generation.
    ##Optional Attributes:
    - `framework (str): Testing framework to use in the generated tests.
    - `aditionalInstructions (str): Additional instructions or requirements for code generation. Defaults to an empty string if not provided.
    - `testExample (str): Test example for the code generation. Defaults to an empty string if not provided.
    '''
    

    language: str
    '''language: A string representing the programming language for which the code needs to be generated.'''
    snippet: str
    '''snippet: A string representing the code snippet or template to be used for code generation.'''
    framework: Optional[str] = ""
    '''framework: A string representing the testing framework to use in the generated tests.'''
    aditionalInstructions: Optional[str] = ""
    '''aditionalInstructions (optional): A string representing any additional instructions or requirements for code generation. Defaults to an empty string if not provided.'''
    testExample: Optional[str] = ""
    '''testExample (optional): A string representing a test example for the code generation. Defaults to an empty string if not provided.'''


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
