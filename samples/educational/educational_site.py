# File: sample_kuedu_site.py
# KuEdu chatbot frontend with '/chat' endpoint

from flask import Flask, render_template_string, request, jsonify
from samples.router.chat_router import run_chatbot

app = Flask('edu_app')

HTML_EDU = '''
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>KuEdu Chatbot</title></head>
<body>
  <h1>Welcome to KuEdu</h1>
  <p>Ask about courses, campus life, student services, and academic counseling.</p>
  <div id="chat-box" class="chat-ui">
    <textarea id="chat_input"></textarea>
    <button onclick="postMsg()">Send</button>
  </div>
  <script>
    async function postMsg() {
      const input = document.getElementById("chat_input").value;
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      alert("Response: " + data.response);
    }
  </script>
</body>
</html>
'''

# Setup local context tracker
context = []
context_limit = 10

@app.route('/')
def edu_index():
    return render_template_string(HTML_EDU)

@app.route('/chat', methods=['POST'])
def edu_chat():
    req = request.get_json() or {}
    message = req.get('message', '')

    # clear context if its after 10 messages
    if len(context) >= context_limit:
        context.clear()

    # Get response from chatbot
    result = run_chatbot(bot_type = "educational", message = message, context = context)

    # Add context
    ctx = {"message_number": len(context) + 1, "prompt": message, "response": result["response"]}
    context.append(ctx)

    return jsonify({ "response": result["response"] })

if __name__ == '__main__':
    # Run on port 5010 by default
    app.run(host='0.0.0.0', port=5009, debug=True)