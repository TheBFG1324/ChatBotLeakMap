# File: finance_site.py
# BTCBank chatbot frontend with '/chat' endpoint

from flask import Flask, render_template_string, request, jsonify
from samples.router.chat_router import run_chatbot

app = Flask("finance_app")

HTML_FINANCE = '''
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>BTCBank Chatbot</title></head>
<body>
  <h1>Welcome to BTCBank</h1>
  <p>Talk about Bitcoin, investments, your portfolio, revenue forecasts, and trading strategies.</p>
  <div id="chat" class="chat-widget">
    <textarea id="input"></textarea>
    <button onclick="send()">Send</button>
  </div>
  <script src="/chat"></script>
</body>
</html>
'''

# Setup local context tracker
context = []
context_limit = 10

@app.route('/')
def finance_index():
    return render_template_string(HTML_FINANCE)

@app.route('/chat', methods=['POST'])
def finance_chat():
    req = request.get_json() or {}
    message = req.get('message', '')

    # clear context if its after 10 messages
    if len(context) >= context_limit:
        context.clear()

    # Get response from chatbot
    result = run_chatbot(bot_type = "finance", message = message, context = context)

    # Add context
    ctx = {"message_number": len(context) + 1, "prompt": message, "response": result["response"]}
    context.append(ctx)

    return jsonify({ "response": result["response"] })

if __name__ == '__main__':
    # Run on port 5010 by default
    app.run(host='0.0.0.0', port=5010, debug=True)