from github import Auth, Github, Repository
import base64
from typing import List
from pydantic import BaseModel


class File(BaseModel):
    """
    Class representing a file in the repository.
    """
    name: str = ""
    content: str = ""
    path: str = ""


def connect_to_repo(repo_name: str, token: str) -> Repository.Repository:
    """
    Connects to a GitHub repository.

    Args:
        repo_name (str): The name of the repository.
        token (str): The authentication token.

    Returns:
        Repository.Repository: The GitHub repository.
    """
    auth = Auth.Token(token)
    github_instance = Github(base_url="https://api.github.com", auth=auth)
    user = github_instance.get_user()
    user_repo = user.get_repo(repo_name)
    return user_repo


def decode_file_contents(repo_name: str, token: str, branch: str = "main") -> List[File]:
    """
    Decodes the content of the files in the repository.

    Args:
        repo_name (str): The name of the repository.
        token (str): The authentication token.
        branch (str, optional): The branch name. Defaults to "main".

    Returns:
        List[File]: List of files with decoded content.
    """
    files: List[File] = fetch_files(repo_name=repo_name, token=token, branch=branch)
    for file in files:
        decoded_content = base64.b64decode(file.content).decode('utf-8', errors='ignore')
        file.content = decoded_content
    return files


def fetch_files(repo_name: str, token: str, branch: str = "main") -> List[File]:
    """
    Retrieves the files from the repository by branch.

    Args:
        repo_name (str): The name of the repository.
        token (str): The authentication token.
        branch (str, optional): The branch name. Defaults to "main".

    Returns:
        List[File]: List of files from the repository.
    """
    repo = connect_to_repo(repo_name=repo_name, token=token)
    contents = repo.get_contents("", ref=branch)
    files: List[File] = []
    while contents:
        file_content = contents.pop()
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = File(name=file_content.name, content=file_content.content, path=file_content.path)
            files.append(file)
    return files
