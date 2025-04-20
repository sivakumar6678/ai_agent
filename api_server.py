from flask import Flask, request, jsonify
import config
from ai_clients.gemini import GeminiClient
import executor

app = Flask(__name__)

# Init Gemini client
ai_client = GeminiClient(
    api_key=config.GEMINI_API_KEY,
    model_name=config.GEMINI_MODEL_NAME
)
# api_server.py (backend update)

# api_server.py (backend update)

@app.route('/agent', methods=['POST'])
def handle_task():
    try:
        data = request.get_json()
        task = data.get("task", "").strip()

        if not task:
            return jsonify({"error": "'task' is required."}), 400

        # Step 1: Refine the prompt
        refined_prompt = ai_client.refine_prompt(task)

        # Step 2: Generate code using the refined prompt (language detection handled internally)
        code = ai_client.generate_code(refined_prompt)
        if not code:
            return jsonify({"error": "Code generation failed."}), 500

        # Step 3: Execute code
        success, output = executor.execute_code(code,language=ai_client.detect_language(code))

        return jsonify({
            "refined_prompt": refined_prompt,
            "code": code,
            "success": success,
            "output": output
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000)
