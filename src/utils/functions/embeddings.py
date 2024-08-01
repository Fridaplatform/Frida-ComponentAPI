from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter
)
from fastapi import HTTPException
import tiktoken
from typing import List, Dict, Tuple

load_dotenv(".env")

languages = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".java": Language.JAVA,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".swift": Language.SWIFT,
    ".cpp": Language.CPP,
    ".c": Language.C,
    ".go": Language.GO,
    ".html": Language.HTML,
    ".php": Language.PHP,
    ".kt": Language.KOTLIN,
}

tokenizer = tiktoken.get_encoding("cl100k_base")

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_API_BASE"),
)


def count_tokens(prompt: str) -> int:
    """Calculates the number of tokens in a prompt

    Args:
        prompt (str): Prompt to be counted

    Returns:
        int: Number of tokens in the prompt
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))


# Function to generate embeddings for the given text using a specified model
def generate_embeddings(text: str = "", model: str = "OpenAIEmbeddings") -> List[float]:
    """
    Generate embeddings for the input text using the specified model.

    Args:
        text (str): The input text for which embeddings are generated.
        model (str): The model to use for generating embeddings.

    Returns:
        str: The embedding data of the input text based on the specified model.
    """
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def generate_code_context(code_segment: str = "", file_name: str = "") -> Dict:
    """
    Generate a brief, comprehensive explanation of a given code segment.

    This function interacts with the OpenAI API to obtain a concise,
    understandable context for a given code segment, limited to 80 words.

    Parameters:
    code_segment (str): The segment of code to be explained.
    file_name (str): The name of the file containing the code segment.

    Returns:
    dict: A dictionary containing the filename and the explanation of the code segment.
    """

    # Requesting the OpenAI API to generate a description of the code segment
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL_NAME"),
        messages=[
            {
                "role": "system", "content": "Add general context to code segments to make them more understandable."
            },
            {
                "role": "system", "content": "Please provide a brief description of what the code does."
            },
            {
                "role": "system", "content": "Don’t include code in your answer."
            },
            {
                "role": "system", "content": "Provide a comprehensive explanation."
            },
            {
                "role": "system", "content": "Limit your response to maximum 80 words."
            },
            {
                "role": "user", "content": f"Here is the code segment: {code_segment}."
            }
        ]
    )

    # Creating metadata with the filename and the explanation of the code segment
    metadata = {
        "Filename": file_name,
        "Explanation": response.choices[0].message.content
    }

    return metadata


def generate_response(query: str = "", code_segment: str = "", file_name: str = ""):
    """
    Generates a response based on the user's query, a provided code segment, and a file name.

    Parameters:
    - query (str): The user's query or question.
    - code_segment (str): The code segment to include in the response.
    - file_name (str): The name of the file associated with the code segment.

    Returns:
    - response: The generated response from the OpenAI API.
    """
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL_NAME"),
        messages=[
            {
                "role": "system",
                "content": (
                    "Respond to the user's question with the provided code segment if relevant. "
                    "If the code segment is not sufficient to answer the question, provide the best possible response. "
                    "Include the file name in your response. "
                    f"Here is the code segment: {code_segment}. "
                    f"Here is the file name: {file_name}."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ],
    )
    return response


def unsupported_extension(file_name: str = "", file_content: str = "", file_path: str = ""):
    """
    Splits the file content into chunks if it exceeds a certain number of tokens.

    Args:
        file_name (str): The name of the file.
        file_content (str): The content of the file.
        file_path (str): The path of the file.

    Returns:
        List[Tuple[str, str, str]]: A list of tuples containing the file name, content chunk, and file path.
    """
    tokens = count_tokens(prompt=file_content)
    if tokens < 1500:
        return [(file_name, file_content, file_path)]
    else:
        content_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            encoding="cl100k_base", chunk_size=1500, chunk_overlap=100
        )
        contents = content_splitter.split_text(file_content)
        all_chunks = [(file_name, content, file_path) for content in contents]
        return all_chunks


def splitter(file_name: str = "", file_content: str = "",
             file_path: str = "") -> List[Tuple[Dict, str, str, List[float]]] | List[Tuple[str, str, str]]:
    """
    Splits a file content into smaller chunks based on the file extension.

    Args:
        file_name (str): The name of the file.
        file_content (str): The content of the file.
        file_path (str): The path of the file.

    Returns:
        List[Tuple[Dict, str, str, List[float]]] | List[Tuple[str, str, str]]:
            A list of tuples, where each tuple contains:
            - context (Dict): Metadata including a brief explanation of the chunk.
            - chunk_content (str): The content of the chunk.
            - file_path (str): The path of the file.
            - embedding (List[float]): The embedding generated for the chunk.
        Or, in the case of an unsupported file extension, a list of tuples with:
            - file_name (str): The name of the file.
            - file_content (str): The content of the file.
            - file_path (str): The path of the file.
    """
    try:
        # Get the file extension
        file_extension = os.path.splitext(file_name)[1]

        # Check if the language is supported
        if file_extension not in languages:
            # TODO: Add support for other file extensions like CSS or JSON
            if file_extension not in [".md"]:
                return unsupported_extension(file_name=file_name, file_content=file_content, file_path=file_path)

        # Create a text splitter based on the file extension
        code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=languages[file_extension], chunk_size=900, chunk_overlap=100
        )

        all_splitters = []

        # Split the file content into chunks
        docs = code_splitter.create_documents([file_content])

        # Append each chunk to the list of splitters
        for doc in docs:
            context_chunk: Dict = generate_code_context(code_segment=doc.page_content, file_name=file_name)
            embedding: List[float] = generate_embeddings(f"Context: {context_chunk} Chunk: {doc.page_content}")
            all_splitters.append((context_chunk, doc.page_content, file_path, embedding))

        return all_splitters

    except Exception as e:
        raise HTTPException(status_code=500, detail="Unsupported file extension") from e
