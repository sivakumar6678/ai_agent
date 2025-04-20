# executor.py
"""
Handles saving, compiling (if necessary), and executing code for various languages.
"""
import subprocess
import os
import config
import sys
from typing import Tuple, List, Optional

def _get_language_config(language: str) -> Optional[dict]:
    """Gets the configuration for the specified language."""
    lang = language.lower()
    return config.SUPPORTED_LANGUAGES.get(lang)

def _save_code(code: str, filename: str) -> bool:
    """Saves the code to a file."""
    try:
        # Ensure the directory exists
        os.makedirs(config.CODE_DIR, exist_ok=True)
        filepath = os.path.join(config.CODE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"{config.EMOJI_INFO} Code saved to '{filepath}'")
        return True
    except IOError as e:
        print(f"{config.EMOJI_ERROR} Error saving code to file {filename}: {e}", file=sys.stderr)
        return False

def _run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
    """Runs a shell command and captures its output."""
    try:
        # print(f"{config.EMOJI_INFO} Running command: {' '.join(command)}") # Debug command
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit code
            cwd=cwd # Current working directory
        )
        if process.returncode == 0:
            return True, process.stdout.strip()
        else:
            # Combine stdout and stderr for better error context
            error_output = f"Error executing: {' '.join(command)}\n"
            if process.stdout:
                 error_output += f"STDOUT:\n{process.stdout.strip()}\n"
            if process.stderr:
                 error_output += f"STDERR:\n{process.stderr.strip()}"
            return False, error_output.strip()

    except FileNotFoundError:
        error_msg = f"Error: Command '{command[0]}' not found. Is it installed and in PATH?"
        print(f"{config.EMOJI_ERROR} {error_msg}", file=sys.stderr)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error running command {' '.join(command)}: {e}"
        print(f"{config.EMOJI_ERROR} {error_msg}", file=sys.stderr)
        return False, error_msg

def execute_code(code: str, language: str) -> Tuple[bool, str]:
    """
    Saves, compiles (if needed), and executes the given code.

    Args:
        code: The source code string.
        language: The programming language (e.g., 'python', 'javascript').

    Returns:
        A tuple containing:
            - bool: True if execution was successful, False otherwise.
            - str: The standard output of the script if successful,
                   or the error message (stderr/stdout) if failed.
    """
    lang_config = _get_language_config(language)
    if not lang_config:
        return False, f"Language '{language}' is not supported."

    filename = lang_config["filename"]
    filepath = os.path.join(config.CODE_DIR, filename)
    
    # Special handling for Java: Check if code contains "class Main"
    if language == "java" and "class Main" not in code:
         # This check is basic. A mismatch between saved filename and public class name WILL cause javac error.
         # The GeminiClient tries to mitigate this, but it's not foolproof.
         print(f"{config.EMOJI_ERROR} Warning: Java code does not contain 'class Main'. Compilation will likely fail.", file=sys.stderr)
         # Return error early to avoid confusing compilation errors? Or let it fail? Let it fail for now.
         # return False, "Java source code must contain 'public class Main {...}' to match the filename 'Main.java'."

    if not _save_code(code, filename):
        return False, f"Failed to save code to {filepath}."

    # --- Compilation Step (if required) ---
    if "compile_command" in lang_config:
        compile_cmd_template = lang_config["compile_command"]
        output_executable = lang_config.get("output_executable") # Optional

        # Replace placeholders in the command template
        compile_cmd = [
            part.replace("{filename}", filename).replace("{output_executable}", output_executable or "")
            for part in compile_cmd_template
        ]
        # Remove empty parts resulting from missing optional placeholders
        compile_cmd = [part for part in compile_cmd if part]

        print(f"{config.EMOJI_INFO} Compiling {language} code...")
        compile_success, compile_output = _run_command(compile_cmd, cwd=config.CODE_DIR)

        if not compile_success:
            print(f"{config.EMOJI_ERROR} Compilation failed.", file=sys.stderr)
            # Clean up source file? Maybe not, user might want to inspect it.
            # os.remove(filepath) # Optional cleanup
            return False, f"Compilation Error:\n{compile_output}"
        print(f"{config.EMOJI_SUCCESS} Compilation successful.")
        # print(f"Compiler output:\n{compile_output}") # Show compiler output/warnings if needed

    # --- Execution Step ---
    exec_cmd_template = lang_config["execute_command"]
    output_executable = lang_config.get("output_executable") # Get again for execution
    class_name = lang_config.get("class_name") # For Java

    # Replace placeholders
    exec_cmd = [
        part.replace("{filename}", filename)
            .replace("{output_executable}", output_executable or "")
            .replace("{class_name}", class_name or "")
        for part in exec_cmd_template
    ]
    exec_cmd = [part for part in exec_cmd if part] # Clean empty parts

    print(f"{config.EMOJI_RUN} Executing {language} code...")
    exec_success, exec_output = _run_command(exec_cmd, cwd=config.CODE_DIR)

    # --- Cleanup (Optional) ---
    # You might want to remove the source file and executable after execution
    # try:
    #     if os.path.exists(filepath):
    #         os.remove(filepath)
    #     if output_executable and language in ["c++"]:
    #           executable_path = os.path.join(config.CODE_DIR, output_executable)
    #           if os.path.exists(executable_path):
    #                os.remove(executable_path)
    #     if language == "java":
    #           class_file = os.path.join(config.CODE_DIR, f"{class_name}.class")
    #           if os.path.exists(class_file):
    #                os.remove(class_file)
    # except OSError as e:
    #     print(f"{config.EMOJI_INFO} Warning: Could not clean up generated files: {e}", file=sys.stderr)


    if exec_success:
        print(f"{config.EMOJI_SUCCESS} Execution finished.")
        return True, exec_output
    else:
        print(f"{config.EMOJI_ERROR} Execution failed.", file=sys.stderr)
        return False, f"Runtime Error:\n{exec_output}"