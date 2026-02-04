#!/usr/bin/env python3
"""
AgentMail Webhook Server
Receives verification emails in real-time
"""
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Store received emails in memory (or could use Redis/DB)
received_emails = []

@app.route('/webhook/agentmail', methods=['POST'])
def agentmail_webhook():
    """Handle incoming AgentMail webhook"""
    try:
        payload = request.json
        
        # Log the webhook
        timestamp = datetime.utcnow().isoformat()
        email_data = {
            'timestamp': timestamp,
            'from': payload.get('from'),
            'to': payload.get('to'),
            'subject': payload.get('subject'),
            'text': payload.get('text'),
            'html': payload.get('html'),
            'message_id': payload.get('message_id'),
        }
        
        received_emails.append(email_data)
        
        # Save to file for persistence
        with open('webhook_emails.json', 'w') as f:
            json.dump(received_emails, f, indent=2)
        
        print(f"📬 Webhook received: {email_data['subject']} from {email_data['from']}")
        
        return jsonify({'status': 'received'}), 200
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/latest', methods=['GET'])
def get_latest_email():
    """Get the most recent email"""
    if received_emails:
        return jsonify(received_emails[-1]), 200
    return jsonify({'error': 'No emails received'}), 404

@app.route('/webhook/all', methods=['GET'])
def get_all_emails():
    """Get all received emails"""
    return jsonify(received_emails), 200

@app.route('/webhook/clear', methods=['POST'])
def clear_emails():
    """Clear all stored emails"""
    global received_emails
    received_emails = []
    if os.path.exists('webhook_emails.json'):
        os.remove('webhook_emails.json')
    return jsonify({'status': 'cleared'}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'emails_received': len(received_emails)
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    print(f"🚀 Webhook server starting on port {port}")
    print(f"📬 Endpoint: http://localhost:{port}/webhook/agentmail")
    app.run(host='0.0.0.0', port=port, debug=False)
