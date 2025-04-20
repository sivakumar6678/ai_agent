# api_server.py

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

@app.route('/agent', methods=['POST'])
def handle_task():
    try:
        data = request.get_json()
        task = data.get("task", "").strip()
        language = data.get("language", "").strip().lower()

        if not task or not language:
            return jsonify({"error": "Both 'task' and 'language' are required."}), 400

        # Generate code
        code = ai_client.generate_code(task, language)
        if not code:
            return jsonify({"error": "Code generation failed."}), 500

        # Execute code
        success, output = executor.execute_code(code, language)

        return jsonify({
            "code": code,
            "success": success,
            "output": output
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000)
