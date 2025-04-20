# main.py
"""
Main CLI interface for the AI Code Agent.
Handles user interaction, language detection, code generation, execution, and retries.
"""

import sys
import os
import config
from ai_clients.gemini import GeminiClient
import executor # Assuming executor.py is in the same directory orPYTHONPATH

def detect_or_ask_language(user_prompt: str) -> str | None:
    """
    Detects the programming language from the prompt or asks the user.

    Args:
        user_prompt: The user's input task description.

    Returns:
        The detected or chosen language (lowercase), or None if detection fails
        and the user doesn't choose.
    """
    prompt_lower = user_prompt.lower()
    detected_language = None

    # Try keyword detection
    for lang, details in config.SUPPORTED_LANGUAGES.items():
        for keyword in details["keywords"]:
            # Use word boundaries or specific phrases for better accuracy
            if f" {keyword} " in prompt_lower or \
               prompt_lower.startswith(f"{keyword} ") or \
               prompt_lower.endswith(f" {keyword}") or \
               prompt_lower == keyword or \
               f"generate {keyword}" in prompt_lower or \
               f"write {keyword}" in prompt_lower:
                detected_language = lang
                break
        if detected_language:
            break

    if detected_language:
        print(f"{config.EMOJI_INFO} Detected language: {detected_language.capitalize()}")
        return detected_language
    else:
        # Ask the user
        print(f"{config.EMOJI_QUESTION} Could not automatically detect the language.")
        print("Please choose a language:")
        lang_list = list(config.SUPPORTED_LANGUAGES.keys())
        for i, lang_name in enumerate(lang_list):
            print(f"  {i + 1}. {lang_name.capitalize()}")

        while True:
            try:
                choice = input(f"Enter number (1-{len(lang_list)}) or language name: ").strip().lower()
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(lang_list):
                        chosen_language = lang_list[index]
                        print(f"{config.EMOJI_INFO} Using language: {chosen_language.capitalize()}")
                        return chosen_language
                    else:
                        print(f"{config.EMOJI_ERROR} Invalid number. Please try again.")
                elif choice in config.SUPPORTED_LANGUAGES:
                     chosen_language = choice
                     print(f"{config.EMOJI_INFO} Using language: {chosen_language.capitalize()}")
                     return chosen_language
                else:
                     print(f"{config.EMOJI_ERROR} Invalid input. Please enter a valid number or language name from the list.")
            except ValueError:
                print(f"{config.EMOJI_ERROR} Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                 print(f"\n{config.EMOJI_STOP} Language selection cancelled.")
                 return None


def main():
    """Main function to run the CLI agent."""
    print("--- AI Code Agent ---")

    # Initialize Gemini Client
    try:
        ai_client = GeminiClient(
            api_key=config.GEMINI_API_KEY,
            model_name=config.GEMINI_MODEL_NAME
        )
    except SystemExit: # Catch exit from GeminiClient init if API key is missing
        return # Exit gracefully

    while True:
        try:
            user_task = input("\nEnter your coding task (or type 'quit' to exit): ").strip()
            if user_task.lower() == 'quit':
                break
            if not user_task:
                continue

            # 1. Detect or Ask Language
            language = detect_or_ask_language(user_task)
            if language is None:
                print(f"{config.EMOJI_STOP} Cannot proceed without a language.")
                continue  # Ask for a new task

            # 2. Refine the prompt (send to Gemini API)
            refined_prompt = ai_client.refine_task(user_task)  # Assuming GeminiClient has this method

            # Show refined task and ask for approval
            print(f"\n🔍 Refined Task:\n{refined_prompt}")
            approval = input("\n✅ Do you want to proceed with this task? (y/n): ").lower()
            if approval != 'y':
                print("❌ Task cancelled by user.")
                continue  # Ask for a new task

            # --- Generation and Execution Loop ---
            generated_code = None
            last_error = None
            attempt = 0
            max_automatic_retries = 1  # Try to fix automatically once

            while True:  # Loop for generation, execution, and retries
                attempt += 1
                print(f"\n--- Attempt {attempt} ---")

                # 3. Generate or Fix Code
                generated_code = ai_client.generate_code(refined_prompt, language)

                if not generated_code:
                    print(f"{config.EMOJI_ERROR} Failed to get code from AI. Please try again or refine your task.")
                    break  # Break inner loop, go back to asking for task

                # 4. Show Code and Ask for Confirmation
                print(f"\n{config.EMOJI_CODE} Generated {language.capitalize()} Code:")
                print("-" * 30)
                print(generated_code)
                print("-" * 30)

                try:
                    confirm = input(f"{config.EMOJI_QUESTION} Execute this code? (y/n): ").strip().lower()
                except KeyboardInterrupt:
                    print(f"\n{config.EMOJI_STOP} Execution cancelled by user.")
                    break  # Break inner loop, go back to asking for task

                if confirm != 'y':
                    print(f"{config.EMOJI_INFO} Execution skipped.")
                    break  # Break inner loop, go back to asking for task

                # 5. Execute Code
                success, output_or_error = executor.execute_code(generated_code, language)

                # 6. Handle Result and Feedback
                if success:
                    print(f"\n{config.EMOJI_SUCCESS} Execution successful!")
                    if output_or_error:
                        print("--- Output ---")
                        print(output_or_error)
                        print("--------------")
                    else:
                        print("(No output)")
                    break  # Success! Break inner loop, go back to asking for task
                else:
                    print(f"\n{config.EMOJI_ERROR} Execution failed!")
                    print("--- Error ---")
                    print(output_or_error)
                    print("-------------")
                    
                    feedback = input("\nWas the task successful? (y/n): ").lower()

                    if feedback != 'y':
                        reason = input("❌ What went wrong? Please describe: ")
                        print("🔁 Refining and retrying...")
                        refined_prompt = refine_task_with_reason(refined_prompt, reason)
                        continue  # Retry the task with the refined prompt
                    else:
                        break  # If successful, exit the loop

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n{config.EMOJI_ERROR} An unexpected error occurred: {e}", file=sys.stderr)
            print("Restarting task input...")

    print("\n--- AI Code Agent Finished ---")

def refine_task_with_reason(refined_prompt, reason):
    # Add your logic to refine the prompt based on the reason
    refined_prompt += f"\nIssue: {reason}"
    return refined_prompt


if __name__ == "__main__":
    # Create code directory if it doesn't exist
    try:
        os.makedirs(config.CODE_DIR, exist_ok=True)
    except OSError as e:
         print(f"{config.EMOJI_ERROR} Could not create code directory '{config.CODE_DIR}': {e}", file=sys.stderr)
         sys.exit(1)
         
    main()