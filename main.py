# main.py

from ai_clients.gemini import get_gemini_response
from executor import execute_code

def generate_and_execute(task):
    prompt = f"Generate Python code to: {task}"
    print("\n🤖 Generating code from Gemini...")
    code = get_gemini_response(prompt)

    print("\n📜 Generated Code:\n")
    print(code)

    approval = input("\n✅ Do you want to execute this code? (yes/no): ").lower()
    if approval == "yes":
        output = execute_code(code)
        if "Error" in output or "Traceback" in output:
            print("\n💥 Execution Error:\n")
            print(output)
            retry = input("\n🔁 Do you want me to try fixing the code and re-run? (yes/no): ").lower()
            if retry == "yes":
                fix_prompt = f"""Fix the following Python code and correct the issue.

Code:
{code}

Error:
{output}

Return only the corrected Python code without extra explanation.
"""
                fixed_code = get_gemini_response(fix_prompt)
                print("\n🛠️ Fixed Code:\n")
                print(fixed_code)
                final_output = execute_code(fixed_code)
                print("\n⚙️ Final Execution Output:\n")
                print(final_output)
            else:
                print("❌ Retry skipped.")
        else:
            print("\n⚙️ Execution Output:\n")
            print(output)
    else:
        print("❌ Execution canceled.")

def main():
    print("👋 Welcome to the Gemini AI Agent!")
    task = input("📝 What task should I perform (e.g., 'Create a calculator')?\n> ")
    generate_and_execute(task)

if __name__ == "__main__":
    main()
