from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({'status': 'healthy', 'message': 'SafeDrive API is running'})

@app.route('/api/v1/health')
def api_health():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=False, host='0.0.0.0', port=port)