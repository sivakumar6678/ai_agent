# ai_clients/gemini.py
"""
Handles interaction with the Google Gemini API.
"""
import google.generativeai as genai
import config
import sys # For error messages

class GeminiClient:
    """Client for generating and fixing code using the Gemini API."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initializes the Gemini client.

        Args:
            api_key: The Google AI API key.
            model_name: The name of the Gemini model to use.
        """
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            print(f"{config.EMOJI_ERROR} Error: Gemini API Key not configured in config.py or environment variables.", file=sys.stderr)
            sys.exit(1) # Exit if API key is not set

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.generation_config = genai.types.GenerationConfig(
                temperature=config.TEMPERATURE,
                max_output_tokens=config.MAX_OUTPUT_TOKENS,
            )
            print(f"{config.EMOJI_INFO} Gemini client initialized successfully with model '{model_name}'.")
        except Exception as e:
            print(f"{config.EMOJI_ERROR} Failed to initialize Gemini client: {e}", file=sys.stderr)
            sys.exit(1)

    def _extract_code(self, text: str, language: str) -> str:
        """
        Extracts the code block from the Gemini response.
        Handles markdown code fences (```language ... ```) or raw code.
        """
        # Simple extraction: find the first code block or assume the whole response is code
        # More robust parsing might be needed depending on model's verbosity
        code_block_marker = f"```{language}"
        fallback_marker = "```"
        
        if code_block_marker in text:
            start = text.find(code_block_marker) + len(code_block_marker)
            end = text.find("```", start)
            code = text[start:end].strip()
        elif fallback_marker in text:
             # Find the first ``` block
            start = text.find(fallback_marker) + len(fallback_marker)
             # Skip potential language name if present (e.g., ```python)
            if text[start:].lstrip().startswith(language):
                 start = text.find('\n', start) + 1 # Move past the language line
            elif text[start] == '\n':
                 start += 1 # Move past the newline after ```
            
            end = text.find("```", start)
            if start != -1 and end != -1:
                 code = text[start:end].strip()
            else: # If no closing ``` found, assume rest is code
                 code = text[start:].strip()

        else:
            # If no markers, assume the whole response might be code (less reliable)
            code = text.strip()
            
        # Basic cleanup for Java class names - ensure it contains 'class Main' if Java
        if language == "java" and "class Main" not in code:
             print(f"{config.EMOJI_INFO} Warning: Generated Java code does not contain 'class Main'. Execution might fail.", file=sys.stderr)
             # Attempt a basic wrap if it looks like just the method body was generated
             if "public static void main" in code and not code.strip().startswith("import") and not code.strip().startswith("package"):
                  print(f"{config.EMOJI_INFO} Attempting to wrap Java code in 'Main' class.")
                  code = f"public class Main {{\n    {code}\n}}"


        return code

    def generate_code(self, prompt: str, language: str) -> str | None:
        """
        Generates code based on the given prompt and language.

        Args:
            prompt: The user's request or task description.
            language: The target programming language.

        Returns:
            The generated code as a string, or None if generation failed.
        """
        full_prompt = f"""
        Generate {language} code for the following task:
        Task: "{prompt}"

        Please provide only the code, without any explanation or introduction, unless the explanation is part of the code comments.
        Ensure the code is complete and runnable.
        For Java, the main class should be named 'Main' and contain the public static void main(String[] args) method.
        For C++, include necessary headers and a main function.
        """
        print(f"{config.EMOJI_GENERATE} Generating {language} code...")
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            # Check for safety ratings or blocks if necessary
            # print(response.prompt_feedback) # For debugging safety issues

            if not response.candidates:
                 print(f"{config.EMOJI_ERROR} Code generation failed. No response candidates.", file=sys.stderr)
                 return None
                 
            generated_text = response.text
            # print(f"Raw response:\n----\n{generated_text}\n----") # Debug raw output
            
            extracted_code = self._extract_code(generated_text, language)
            
            if not extracted_code:
                 print(f"{config.EMOJI_ERROR} Code generation failed. Could not extract code from response.", file=sys.stderr)
                 # print(f"--- Raw Response ---\n{generated_text}\n--- End Raw Response ---") # Show response if extraction fails
                 return None

            return extracted_code

        except Exception as e:
            print(f"{config.EMOJI_ERROR} Error during code generation: {e}", file=sys.stderr)
            return None

    def fix_code(self, task: str, language: str, broken_code: str, error_message: str) -> str | None:
        """
        Attempts to fix the provided code based on the error message.

        Args:
            task: The original user task.
            language: The programming language of the code.
            broken_code: The code that produced an error.
            error_message: The error message captured during execution.

        Returns:
            The potentially fixed code as a string, or None if fixing failed.
        """
        fix_prompt = f"""
        The following {language} code was generated for the task "{task}".
        However, it produced an error when executed.

        Original Task: "{task}"

        Broken Code:
        ```
        {broken_code}
        ```

        Error Message:
        ```
        {error_message}
        ```

        Please fix the {language} code to resolve the error and fulfill the original task.
        Provide only the corrected, complete, and runnable code, without explanations.
        For Java, ensure the main class is 'Main'.
        For C++, ensure necessary headers and a main function are present.
        """
        print(f"{config.EMOJI_RETRY} Attempting to fix {language} code...")
        try:
            response = self.model.generate_content(
                fix_prompt,
                generation_config=self.generation_config
            )
            if not response.candidates:
                 print(f"{config.EMOJI_ERROR} Code fixing failed. No response candidates.", file=sys.stderr)
                 return None

            generated_text = response.text
            extracted_code = self._extract_code(generated_text, language)

            if not extracted_code:
                 print(f"{config.EMOJI_ERROR} Code fixing failed. Could not extract code from response.", file=sys.stderr)
                 # print(f"--- Raw Response ---\n{generated_text}\n--- End Raw Response ---") # Show response if extraction fails
                 return None

            return extracted_code

        except Exception as e:
            print(f"{config.EMOJI_ERROR} Error during code fixing: {e}", file=sys.stderr)
            return None