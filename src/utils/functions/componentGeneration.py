from openai import OpenAI
from fastapi import HTTPException

import re
from typing import Optional
from utils import schemas

# Create a new instance of the AzureOpenAI client
client = OpenAI(
    base_url="http://198.145.126.112:8080/v1",
    api_key="-"
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

    general_prompt = promptManagement + "\n" + codeExample
    
    try:
        messages = [
            {
                "role": "system",
                "content": general_prompt,
            },
            {
                "role": "user",
                "content": prompt.prompt
            }
        ]
        
        chat_completion = client.chat.completions.create(
            model="tgi",
            messages=messages,
            stream=False,
            temperature=1,
            max_tokens=200
            )
        
        componentCode = chat_completion.choices[0].message.content
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