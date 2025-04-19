# main.py

from ai_clients.gemini import get_gemini_response
from executor import execute_code
import re

def extract_code_blocks(text):
    """Extracts Python code from triple backtick blocks."""
    code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
    return "\n\n".join(code_blocks).strip() if code_blocks else text.strip()

def main():
    print("👋 Welcome to the Gemini AI Agent!")
    task = input("📝 What task should I perform (e.g., 'Create a calculator')?\n> ")

    prompt = f"Generate Python code to: {task}"
    print("\n🤖 Generating code from Gemini...")
    response = get_gemini_response(prompt)

    print("\n📜 Generated Plan (Raw Response):\n")
    print(response)

    code = extract_code_blocks(response)

    approval = input("\n✅ Do you want to execute this code? (yes/no): ").lower()
    if approval == "yes":
        output = execute_code(code)
        print("\n⚙️ Execution Output:\n")
        print(output)
    else:
        print("❌ Execution canceled.")

if __name__ == "__main__":
    main()
