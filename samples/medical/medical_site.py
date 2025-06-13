# File: sample_medicorp_site.py
# Medicorp chatbot frontend with '/chat' endpoint

from flask import Flask, render_template_string, request, jsonify
from samples.router.chat_router import run_chatbot

app = Flask('medical_app')

HTML_MED = '''
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Medicorp Chatbot</title></head>
<body>
  <h1>Welcome to Medicorp</h1>
  <p>Your source for medical advice, patient history (HIPAA compliant), and health tips.</p>
  <div id="medical-chat" class="chat-interface">
    <textarea></textarea>
    <button onclick="sendMsg()">Send</button>
  </div>
  <script src="/chat"></script>
</body>
</html>
'''

# Setup local context tracker
context = []
context_limit = 10

@app.route('/')
def med_index():
    return render_template_string(HTML_MED)

@app.route('/chat', methods=['POST'])
def med_chat():
    content = request.get_json() or {}
    message = content.get('message', '')
    
    # clear context if its after 10 messages
    if len(context) >= context_limit:
        context.clear()
    
    # Get response from chatbot
    result = run_chatbot(bot_type = "medical", message = message, context = context)

    # Add context
    ctx = {"message_number": len(context) + 1, "prompt": message, "response": result["response"]}
    context.append(ctx)

    return jsonify({ "response": result["response"] })

if __name__ == '__main__':
    # Run on port 5010 by default
    app.run(host='0.0.0.0', port=5011, debug=True)