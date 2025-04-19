import subprocess
import os
import re

def clean_code(code):
    # Remove markdown blocks for any language (e.g., ```python, ```javascript, etc.)
    code = re.sub(r"```(?:\w+)?", "", code)  # matches any language after ```
    code = code.replace("```", "")  # removes closing ```
    
    # Remove non-code introductory text (if any)
    code = re.sub(r"^[^\w]+", "", code)  # Remove any non-code characters at the beginning
    
    return code.strip()

def execute_code(code, filename="generated_script"):
    # Clean the markdown formatting and introductory text
    code = clean_code(code)

    file_extension = ".py"  # Default extension is Python

    # Detect the language from the code and choose the file extension accordingly
    if "def " in code:  # if it's Python code
        file_extension = ".py"
    elif "function" in code:  # simple heuristic for JavaScript
        file_extension = ".js"
    elif "#include" in code:  # simple heuristic for C/C++
        file_extension = ".cpp"
    elif "import" in code:  # Java or similar languages with imports
        file_extension = ".java"
    
    # Save the cleaned code to a file with appropriate extension
    file_path = f"{filename}{file_extension}"
    
    with open(file_path, "w") as f:
        f.write(code)

    try:
        # Execute the code based on the file type
        if file_extension == ".py":
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif file_extension == ".js":
            result = subprocess.run(
                ["node", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif file_extension == ".cpp":
            subprocess.run(["g++", file_path, "-o", "generated_program"])
            result = subprocess.run(
                ["./generated_program"],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif file_extension == ".java":
            subprocess.run(["javac", file_path])  # Compile Java code
            result = subprocess.run(
                ["java", file_path.replace(".java", "")],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            return "❌ Unsupported language for execution."

        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "⏱️ Execution timed out."
    except Exception as e:
        return f"❌ Unexpected error: {e}"
