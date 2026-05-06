from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'compliance-training'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
