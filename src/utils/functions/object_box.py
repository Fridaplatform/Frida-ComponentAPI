from embeddings import generate_embeddings, generate_response
import utils.objectboxDB.ob as ob
from faiss_search import search_embeddings
from typing import List, Dict, Tuple
from embeddings import splitter


def upload_text_file_to_objectbox(file_name: str = "", file_text: str = "",
                                  file_path: str = "", repo_name: str = "",
                                  repo_branch: str = "") -> List[Dict[str, str]]:
    """
    Uploads a text file to ObjectBox by splitting it into chunks and generating embeddings for each chunk.

    Args:
        file_name (str): The name of the file.
        file_text (str): The text content of the file.
        file_path (str): The path of the file.
        repo_name (str): The name of the repository.
        repo_branch (str): The branch of the repository.

    Returns:
        List[Dict[str, str]]: A list of results for each chunk uploaded, including any errors.
    """
    # Initialize a list to store the results of each chunk upload
    upload_results: List[Dict[str, str]] = []

    # Extract chunks from the file using a splitter
    try:
        chunks: List[Tuple[Dict, str, str, List[float]]] | List[Tuple[str, str, str]] = splitter(
            file_name=file_name, file_content=file_text, file_path=file_path)
    except Exception as e:
        # Handle errors during file splitting and return the error result
        error_result = {"file_name": file_name, "status": "error", "error": str(e)}
        upload_results.append(error_result)
        return upload_results

    # Process and upload each chunk
    try:
        for chunk in chunks:
            try:
                # Extract the name, context, text, path and embedding from the chunk
                chunk_name = chunk[0]
                chunk_context = chunk[0]
                # Extract metadata from the chunk
                if type(chunk[0]) is dict:
                    chunk_name = chunk[0]["Filename"]
                    chunk_context = chunk[0]["Explanation"]
                chunk_text = chunk[1]
                chunk_path = chunk[2]
                chunk_embedding = chunk[3]

                # Create a TextChunk object with the chunk data
                text_file_chunk = ob.TextChunk(
                    repository_name=repo_name,
                    repository_branch=repo_branch,
                    file_name=chunk_name,
                    context=chunk_context,
                    text=chunk_text,
                    path=chunk_path,
                    embedding=chunk_embedding
                )

                # Store the chunk in ObjectBox
                ob.text_chunk.put(text_file_chunk)

                # Append the success result for the chunk
                upload_results.append({"file_name": chunk_name, "status": "uploaded", "content": chunk_text})
            except Exception as e:
                # Handle errors during chunk upload and append the error result
                chunk_name = file_name
                error_result = {"file_name": chunk_name, "status": "error", "error": str(e)}
                upload_results.append(error_result)
    except Exception as e:
        # Handle any unexpected errors during the chunk processing loop
        error_result = {"file_name": file_name, "status": "error", "error": str(e)}
        upload_results.append(error_result)

    # Return the list of upload results
    return upload_results


def search_in_text_files(repo_name: str = "", repo_branch: str = "main", user_prompt: str = ""):
    """
    This function returns the most relevant document to the user prompt through embedding
    using the 'text-embedding-ada-002' model from OpenAI and limits the results to 1.

    Args:
        repo_name (str): The repository name for the search.
        repo_branch (str): The repository branch for the search.
        user_prompt (str): The prompt provided by the user.

    Returns:
        str: The most relevant document to the user prompt.

    Note:
        The function is still in progress and not yet complete.
        Currently, it filters text chunks by repository name and branch,
        generates embeddings using Azure OpenAI, and performs FAISS search.
        It also generates partial responses using Azure OpenAI and Ollama models.
    """
    # Generate an embedding for the prompt and retrieve the most relevant doc
    if len(ob.text_chunk.get_all()) > 0:
        # embedding = embedding_response(content=user_prompt)
        embedding_openai = generate_embeddings(user_prompt)

        # Filter by repository name and branch name
        query_filter = ob.text_chunk.query(ob.TextChunk.repository_name.equals(repo_name) &
                                           ob.TextChunk.repository_branch.equals(repo_branch)).build()
        query_results = query_filter.find()

        # Prepare data
        query_embeddings = [query_result.embedding for query_result in query_results]

        # FAISS search of the most similar TextChunk to the user prompt
        index_closer = search_embeddings(embeddings=query_embeddings, query_embedding=embedding_openai,
                                         k=1)

        result = query_results[index_closer[0][0]]

        print("Repo name: ", result.repository_name)
        print("Repo branch: ", result.repository_branch)
        print("File Name: ", result.file_name)
        print("File Path: ", result.path)
        print("File content", result.text)

        # OPENAI response
        response = generate_response(query=user_prompt, code_segment=result.text,
                                     file_name=result.file_name)
        print(response.choices[0].message.content)
