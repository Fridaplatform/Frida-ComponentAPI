from openai import AzureOpenAI
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import re
from typing import Optional
from utils import schemas

# Load environment variables from the .env file
load_dotenv()
OpenAi_Key = os.getenv("OPENAI_API_KEY")
OpenAi_Model = os.getenv("OPENAI_CHAT_MODEL_NAME")
OpenAi_Azure_endPoint = os.getenv("OPENAI_API_BASE")
OpenAi_ApiVersion = os.getenv("OPENAI_API_VERSION")

# Create a new instance of the AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint=OpenAi_Azure_endPoint,
    api_key=OpenAi_Key,
    api_version=OpenAi_ApiVersion
)

def extract_filename(content: str) -> Optional[str]:
    # Define a regex pattern to find filenames with both comment styles
    pattern = r'(?:/\* File:\s+|\s+// File:\s+)([\w\-]+\.js)'
    match = re.search(pattern, content)
    return match.group(1) if match else None

def generateComponent(prompt: schemas.ComponentRequest) -> dict:
    promptManagement = f"""
    You are a code assistant specialized in generating React components. When you receive a {prompt.prompt} from the user, you should:
    Generate the code for a React component based on the prompt, and use Bootstrap to give it it's styles.
    Include documentation for the code, following best practices.
    Always include a comment on the first line specifying the file name the code should have.
    Enclose the entire code block between triple backticks (```), and ensure that this format is always used.
    """

    codeExample = """
    Here is an example of how you should generate the code for the component:

    ```
    /* File: MyComponent.js */
    import React from 'react';
    import 'bootstrap/dist/css/bootstrap.min.css';  // Import Bootstrap CSS

    /**
     * MyComponent - A simple React component.
     * 
     * @returns {JSX.Element} The rendered component.
     */
    export const MyComponent = () => {
        return (
            <div className="container mt-5">
                <div className="alert alert-primary" role="alert">
                    Hello, World!
                </div>
            </div>
        );
    };
    ```
    """
    
    try:
        messages = [
            {
                "role": "system",
                "content": promptManagement,
            },
            {
                "role": "system",
                "content": codeExample,
            },
            {
                "role": "user",
                "content": prompt.prompt
            }
        ]
        
        completion = client.chat.completions.create(
            model=OpenAi_Model,
            messages=messages
        )
        
        componentCode = completion.choices[0].message.content
        file_name = extract_filename(componentCode)
        print('file:', file_name)
        print('code', componentCode)
        results = {
            "File_Name": file_name,
            "Component_Code": componentCode,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
    return results

'''
{
  "prompt": "Create a React component called ButtonComponent that displays a button with the text \"Click Me\". The component should handle a click event that logs \"Button clicked!\" to the console. Include appropriate comments and documentation for the component.",
  "replaces": ""
}

'''