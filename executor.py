# executor.py

import subprocess

def execute_code(code, filename="generated_script.py"):
    """
    Writes code to a file and attempts to execute it.
    Returns stdout or stderr as output.
    """
    with open(filename, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(["python", filename], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
