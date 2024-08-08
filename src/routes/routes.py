from fastapi import APIRouter, HTTPException
from utils.functions import componentGeneration, github_repo_file_decoder, object_box, unitTests
from utils import schemas

router = APIRouter()


@router.post('/componentGeneration', description="Generate React.js components based on the user's given prompt")
def generate_component(request: schemas.ComponentRequest):
    '''
    Generate React.js components based on the user's given prompt

    Args:
        request: The prompt given by the user to generate the React.js component.

    Returns:
        dict: Generated component
    '''

    try:
        component = componentGeneration.generateComponent(request)
        return{'component': component}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e) from e
    

@router.post('/unitTest', description= 'Generate unit tests for the provided code')
def generate_tests(request: schemas.CodeRequest):
    """
    Generate unit tests for the provided code.

    Args:
        request (CodeRequest): The code for which to generate unit tests.

    Returns:
        dict: Generated unit tests.
    """
    try:
        tests = unitTests.generate_unit_test(request) #Generates a unit test for the given request. :param request: the request to generate a unit test for :return: the generated unit test
        return {'tests': tests} #Returns a dictionary containing a single key-value pair. The key is 'tests' and the value is the provided list 'tests'.
    except Exception as e:
        raise HTTPException(status_code=500, detail=e) from e


@router.post("/search", description="Execute a search request in the Text Files.")
async def execute_search_request(request: schemas.ChatSearchRequest):
    """
        Execute a search request in the Text Files.

        Args:
            request (schemas.ChatSearchRequest): The request object containing search data.

        Returns:
            The search results.
        """
    try:

        response = object_box.search_in_text_files(request.repo_name, request.repo_branch,
                                                   request.prompt)
        if response:
            return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error") from e


@router.post("/upload-github-text-files", description="Upload text files from a GitHub repository to ObjectBox")
async def upload_text_files_from_github(request: schemas.GitHubRepository):
    """
    Uploads text files from a GitHub repository to ObjectBox.

    This endpoint decodes the file contents from a specified GitHub repository, processes
    each file by splitting it into chunks and uploading those chunks to ObjectBox.

    Args:
        request (schemas.GitHubRepository): The request object containing the repository name and access token.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary containing the status of the upload for each file.
    """
    try:
        # Decode file contents from the GitHub repository
        files: List[github_repo_file_decoder.File] = github_repo_file_decoder.decode_file_contents(
            repo_name=request.repo_name,
            token=request.token,
            branch=request.branch
        )

        # Initialize a list to store the results of each file upload
        upload_results: List[Dict[str, str]] = []

        # Process and upload each file
        for file in files:
            try:
                # Upload the text file to ObjectBox and append the result
                result = object_box.upload_text_file_to_objectbox(file_name=file.name, file_text=file.content,
                                                                  file_path=file.path, repo_name=request.repo_name,
                                                                  repo_branch=request.branch)
                print(result)
                upload_results.append(result)
            except Exception as e:
                # Append the error result if an exception occurs
                error_result = {"file_name": file.name, "status": "error", "error": str(e)}
                upload_results.append(error_result)

        # Return the upload results
        return {"status": "completed", "results": upload_results}

    except Exception as e:
        # Handle any unexpected exceptions and raise an HTTP 500 error
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
