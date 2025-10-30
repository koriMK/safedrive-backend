from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'SafeDrive API is running',
        'version': '1.0.0'
    })

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'safedrive-backend'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)