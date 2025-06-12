# Example usage:
# crawler = ChatbotCrawler([
#     "http://finance.local", 
#     "http://medical.local", 
#     "http://education.local"
# ])
# crawler.discover_and_register()

# -------------------------------------------------------
# Sample Finance Chatbot API for Testing the Crawler
# File: sample_finance_site.py
# A minimal Flask app serving a finance-themed chatbot UI.

from flask import Flask, render_template_string

app = Flask(__name__)

# Simple HTML page with a textarea and finance keywords
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FinanceCorp Chatbot</title>
</head>
<body>
    <h1>Welcome to FinanceCorp</h1>
    <p>Ask about finance, investment, revenue, profit, or stock trading below:</p>
    <div id="chat-container" class="chat-widget">
        <textarea id="chat-input" placeholder="Type your question..."></textarea>
        <button onclick="sendMessage()">Send</button>
    </div>
    <script>
    function sendMessage() {
        const input = document.getElementById('chat-input').value;
        const response = 'FinanceCorp response to: ' + input;
        alert(response);
    }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    # Run on port 5000 by default
    app.run(host='0.0.0.0', port=5009, debug=True)

# To test:
# 1. Install Flask: pip install Flask
# 2. Run: python sample_finance_site.py
# 3. In another terminal, run your crawler against http://localhost:5000
#    e.g. ChatbotCrawler(['http://localhost:5000']).discover_and_register()
