from openai import OpenAI
from fastapi import HTTPException
from utils import schemas
import re
from typing import Optional

client = OpenAI(
    base_url="http://198.145.126.112:8080/v1",
    api_key="-"
)

def separate_tests(text):
    # Define a regex pattern that captures content for Happy Path and Edge Case
    pattern = r'(?s)Happy Paths\s*(.*?)(?=\s*Edge Case|$)(?:\s*Edge Cases\s*(.*))?'
    
    # Use regex to find matches
    match = re.search(pattern, text)
    
    if match:
        happy_path = match.group(1).strip() if match.group(1) else ""
        edge_case = match.group(2).strip() if match.group(2) else ""
        return {
            "Happy_Paths": f"{{\n{happy_path}\n}}",
            "Edge_Cases": f"{{\n{edge_case}\n}}"
        }
    else:
        # Return empty if no matches are found
        return {
            "Happy_Paths": "{}",
            "Edge_Cases": "{}"
        }

def extract_filename(content: str) -> Optional[str]:
    # Define a regex pattern to find filenames with multiple dot-separated parts and specific extensions
    pattern = r'\b[\w\-]+(?:\.[\w\-]+)*\.(py|js|ts|cpp|cs)\b'
    match = re.search(pattern, content)
    return match.group(0) if match else None


def generate_unit_test(code: schemas.CodeRequest) -> dict:
    """
    Generate unit tests for the given code.

    Args:
        code (str): The code to generate tests for.

    Returns:
        str: Generated unit test code.
    """
    try:
        languagePrompt = ""
        if code.language == 'c#':
            languagePrompt = f"Generate unit tests using Xunit for this function {code.snippet}  with the following criteria:   Test all edge cases: This includes testing negative inputs, zero, and maximum allowed values.  Ensure type error handling: Verify that the function handles incorrect data types appropriately (e.g., strings instead of numbers).  Follow C# coding standards: Write the tests in a clear and consistent manner, adhering to C# coding conventions. Document each test clearly and concisely: Explain what each test is verifying and the expected outcome."
        
        elif code.language == 'python':
            languagePrompt = f"Generate unit tests for the function {code.snippet}  with the following criteria:  Test all edge cases: This includes testing negative inputs, zero, and maximum allowed values. Ensure type error handling: Verify that the function handles incorrect data types appropriately (e.g., strings instead of numbers). Follow PEP 8 style conventions: Write the tests in a clear and consistent manner following PEP 8 guidelines for Python code. Document each test clearly and concisely: Explain what each test is verifying and the expected outcome."

        else:
            languagePrompt = f"Generate unit tests for the function {code.snippet}  with the following criteria:  Test all edge cases: This includes testing negative inputs, zero, and maximum allowed values. Ensure type error handling: Verify that the function handles incorrect data types appropriately (e.g., strings instead of numbers)."

        prompt2 = f" The tests should be written in the {code.language} programming language as specified by the user. It is essential to include the function to test directly in your answer—neither you nor the user should import the function. The {code.snippet} must be present in the generated code for testing. Ensure that {code.snippet} is fully included in the generated code, as it is critical that neither the AI nor the user imports this function."
        
        prompt3 = ""
        if code.framework != "":
            prompt3 = f"Use {code.framework} as the testing framework to generate a up to guidelines test."
        else:
            prompt3 = f"Use the most popular testing framework for {code.language}, to  generate a up to guidelines test."


        prompt4 = ""
        if code.aditionalInstructions != "":
            prompt4 = f"You have to follow the aditional instructions: {code.aditionalInstructions} that the user may add. This instructions may vary, and include details of how many tests are needed, what to use to test."

        prompt5 = ""
        if code.testExample != "":
            prompt5 = f"Use {code.testExample} as an example of how to generate a up to guidelines test. Using it as a template to generate different tests."
            
        prompt6 = "The test you return must include two types of tests: happy paths and edge cases. You must generate at least six tests in total, with three happy paths and three edge cases. Separate the happy path tests from the edge cases, specifying which is which by adding the comment 'Happy Paths' or 'Edge Cases' on top of them (only one time on top of the first test type for each). Include the filename for the generated tests as a comment on the very first line of the code. Respond only with the generated code within a code-block, denoted by ```, and always include the programming language (specified by the user) at the beginning of the code-block. Ensure to document your code, follow best practices, and include comments with the filename and instructions on how to run it. These instructions should always be included as comments at the beginning of the code, detailing the modules or libraries that need to be installed, how to install them, and the necessary commands to run the file. Only respond with the code and its comments—no explanations."

        finalPrompt = languagePrompt + "\n" + prompt2 + "\n" + prompt3 + "\n" + prompt4 + "\n" + prompt5 + "\n" + prompt6 + "\n" + "Do not add any aditional text, only responde with the generated code, it's insctruction, and necessary comments. After finishing the code block with ``` do not add anything more, you should end your answer with ```"

        prompts = [
            {
                "role": "system",
                "content": finalPrompt
            },
            {
                "role": "user",
                "content": code.snippet
            }
        ]
        
            
        completion = client.chat.completions.create( #Generates a unit test for the provided code snippet.
        model="tgi",
            messages=prompts,
            stream=False,
            temperature=0.00000001,
            max_tokens=1024
        )
        test_code = completion.choices[0].message.content
        separated_tests =  separate_tests(test_code)
        file_name = extract_filename(test_code)
        results = {
            "File_Name": file_name,
            "Raw_Test_Code": test_code,
            "Separated_Tests": separated_tests
        }
        
        print(file_name)
        print('code \n' + test_code)
        
    except Exception as e: #Raises an HTTPException with status code 500 and detailed error message, propagating the original exception as the cause.
        raise HTTPException(status_code=500, detail=e) from e
    
    return results #A string representing the generated unit test code.

'''test api route, may modify them when testing
{
  "language": "python",
  "snippet": "def add(num1, num2):\nnum1+num2=response\nprint(response)\nreturn response",
  "framework": "",
  "aditionalInstructions": "",
  "testExample": ""
}

{
  "language": "python",
  "snippet": "def sum_num(x, y):\n return x + y",
  "framework": "behave",
  "aditionalInstructions": "",
  "testExample": ""
}

{
  "language": "javascript",
  "snippet": "function fibonacci(n) {\n  if (n <= 0) return 0;\n  if (n === 1) return 1;\n  let a = 0, b = 1, c;\n  for (let i = 2; i <= n; i++) {\n    c = a + b;\n    a = b;\n    b = c;\n  }\n  return b;\n}",
  "framework": "",
  "aditionalInstructions": "",
  "testExample": ""
}

{
  "language": "typescript",
  "snippet": "function quickSort(array: number[]): number[] {\n  if (array.length <= 1) return array;\n  const pivot = array[array.length - 1];\n  const left: number[] = [];\n  const right: number[] = [];\n\n  for (let i = 0; i < array.length - 1; i++) {\n    if (array[i] < pivot) {\n      left.push(array[i]);\n    } else {\n      right.push(array[i]);\n    }\n  }\n\n  return [...quickSort(left), pivot, ...quickSort(right)];\n}\n\n// Example usage:\nconst array = [3, 6, 8, 10, 1, 2, 1];\nconsole.log(\"Sorted array:\", quickSort(array));",
  "framework": "",
  "aditionalInstructions": "",
  "testExample": ""
}


{
  "language": "c++",
  "snippet": "#include <iostream>\n#include <vector>\n#include <queue>\n#include <climits>\n\nusing namespace std;\n\nvoid dijkstra(int source, vector<vector<pair<int, int>>>& graph, vector<int>& dist) {\n    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;\n    dist[source] = 0;\n    pq.push({0, source});\n\n    while (!pq.empty()) {\n        int u = pq.top().second;\n        pq.pop();\n\n        for (auto& neighbor : graph[u]) {\n            int v = neighbor.first;\n            int weight = neighbor.second;\n\n            if (dist[u] + weight < dist[v]) {\n                dist[v] = dist[u] + weight;\n                pq.push({dist[v], v});\n            }\n        }\n    }\n}\n\nint main() {\n    int numVertices = 5; // Number of vertices in the graph\n    vector<vector<pair<int, int>>> graph(numVertices);\n\n    // Add edges (u, v, weight)\n    graph[0].push_back({1, 10});\n    graph[0].push_back({4, 3});\n    graph[1].push_back({2, 2});\n    graph[1].push_back({4, 4});\n    graph[2].push_back({3, 9});\n    graph[3].push_back({4, 7});\n\n    vector<int> dist(numVertices, INT_MAX);\n    dijkstra(0, graph, dist);\n\n    cout << \"Vertex Distance from Source\\n\";\n    for (int i = 0; i < numVertices; i++) {\n        cout << i << \" \\t\" << dist[i] << \"\\n\";\n    }\n\n    return 0;\n}",
  "framework": "",
  "aditionalInstructions": "",
  "testExample": ""
}

{
  "language": "C#",
  "snippet": "using System;\n\npublic class Program\n{\n    public static void Main()\n    {\n        // Example usage\n        int num1 = 5;\n        int num2 = 10;\n        int result = Add(num1, num2);\n        Console.WriteLine(\"The sum is: \" + result);\n    }\n\n    public static int Add(int num1, int num2)\n    {\n        // Sums two integers and returns the result\n        return num1 + num2;\n    }\n}",
  "framework": "",
  "additionalInstructions": "Test every possible case, happy path, edge cases, etc.",
  "testExample": ""
}


'''