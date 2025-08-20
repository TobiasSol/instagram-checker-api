#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Account Checker Web API
Flask-basierte REST API für die Webseiten-Integration
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import time
import random
from typing import Dict, List, Any
from hikerapi import Client

app = Flask(__name__)
CORS(app)  # Erlaubt Cross-Origin Requests

class WebInstagramChecker:
    def __init__(self):
        self.token = "iax7bn3b5n89rg7wq1s210va208669x6"
        self.client = Client(token=self.token)
    
    def check_single_account(self, username: str) -> Dict[str, Any]:
        """Prüft einen einzelnen Account"""
        try:
            user_info = self.client.user_by_username_v1(username)
            
            if user_info and isinstance(user_info, dict):
                return {
                    'username': username,
                    'is_live': True,
                    'status': 'LIVE',
                    'user_info': {
                        'user_id': user_info.get("pk"),
                        'full_name': user_info.get("full_name", ""),
                        'follower_count': user_info.get("follower_count", 0),
                        'following_count': user_info.get("following_count", 0),
                        'is_private': user_info.get("is_private", False),
                        'is_verified': user_info.get("is_verified", False),
                        'profile_pic': user_info.get("profile_pic_url", ""),
                        'instagram_url': f"https://instagram.com/{username}"
                    }
                }
            else:
                return {
                    'username': username,
                    'is_live': False,
                    'status': 'NOT_AVAILABLE',
                    'error': 'Account existiert nicht oder ist nicht verfügbar'
                }
                
        except Exception as e:
            return {
                'username': username,
                'is_live': False,
                'status': 'ERROR',
                'error': str(e)
            }

# Globale Checker-Instanz
checker = WebInstagramChecker()

@app.route('/')
def home():
    """Einfache Demo-Seite"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instagram Account Checker</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .result { margin: 10px 0; padding: 15px; border-radius: 5px; }
            .live { background: #d4edda; border-left: 5px solid #28a745; }
            .dead { background: #f8d7da; border-left: 5px solid #dc3545; }
            input[type="text"] { width: 300px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .loading { display: none; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Instagram Account Checker</h1>
            <p>Prüfen Sie, ob ein Instagram-Account verfügbar ist:</p>
            
            <div>
                <input type="text" id="username" placeholder="Username eingeben (ohne @)" />
                <button onclick="checkAccount()">Account prüfen</button>
            </div>
            
            <div id="loading" class="loading">⏳ Prüfe Account...</div>
            <div id="result"></div>
        </div>

        <script>
        async function checkAccount() {
            const username = document.getElementById('username').value.trim();
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            
            if (!username) {
                alert('Bitte Username eingeben!');
                return;
            }
            
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/check/' + encodeURIComponent(username));
                const data = await response.json();
                
                loadingDiv.style.display = 'none';
                
                if (data.is_live) {
                    resultDiv.innerHTML = `
                        <div class="result live">
                            <h3>✅ @${data.username} ist verfügbar!</h3>
                            <p><strong>Name:</strong> ${data.user_info.full_name || 'Nicht angegeben'}</p>
                            <p><strong>Follower:</strong> ${data.user_info.follower_count.toLocaleString()}</p>
                            <p><strong>Following:</strong> ${data.user_info.following_count.toLocaleString()}</p>
                            <p><strong>Privat:</strong> ${data.user_info.is_private ? 'Ja' : 'Nein'}</p>
                            <p><strong>Verifiziert:</strong> ${data.user_info.is_verified ? 'Ja' : 'Nein'}</p>
                            <p><a href="${data.user_info.instagram_url}" target="_blank">🔗 Instagram-Profil öffnen</a></p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result dead">
                            <h3>❌ @${data.username} ist nicht verfügbar</h3>
                            <p><strong>Grund:</strong> ${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                resultDiv.innerHTML = `
                    <div class="result dead">
                        <h3>⚠️ Fehler beim Prüfen</h3>
                        <p>Es ist ein Fehler aufgetreten: ${error.message}</p>
                    </div>
                `;
            }
        }
        
        // Enter-Taste Support
        document.getElementById('username').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkAccount();
            }
        });
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/check/<username>')
def check_account_api(username):
    """API Endpoint für einzelne Account-Prüfung"""
    result = checker.check_single_account(username)
    return jsonify(result)

@app.route('/api/check-multiple', methods=['POST'])
def check_multiple_accounts():
    """API Endpoint für mehrere Accounts"""
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if not usernames:
            return jsonify({'error': 'Keine Usernames angegeben'}), 400
        
        results = []
        for username in usernames:
            result = checker.check_single_account(username)
            results.append(result)
            # Kurze Pause zwischen Requests
            time.sleep(random.uniform(0.5, 1.0))
        
        return jsonify({
            'results': results,
            'total_checked': len(usernames),
            'live_count': sum(1 for r in results if r['is_live']),
            'dead_count': sum(1 for r in results if not r['is_live'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API Status Check"""
    return jsonify({
        'status': 'online',
        'service': 'Instagram Account Checker API',
        'version': '1.0'
    })

if __name__ == '__main__':
    # Für lokale Entwicklung
    print("🚀 Instagram Account Checker Web API startet...")
    print("📱 Demo-Seite: http://localhost:5000")
    print("🔗 API-Docs: http://localhost:5000/api/status")
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Für Production (Render, Railway, etc.)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)