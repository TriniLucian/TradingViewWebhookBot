from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_SECRET_KEY")

@app.route('/')
def home():
    return "✅ Webhook server is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("✅ Incoming webhook payload:", data)

        symbol = data.get("symbol")
        side = data.get("action")
        qty = data.get("qty")

        if not all([symbol, side, qty]):
            print("❌ Missing fields in webhook data:", data)
            return jsonify({"error": "Missing required fields"}), 400

        response = place_order(symbol, side, qty)
        return jsonify(response), 200

    except Exception as e:
        print("❌ Webhook processing error:", str(e))
        return jsonify({"error": "Webhook processing failed"}), 500

def place_order(symbol, side, qty):
    url = "https://api.bybit.com/v5/order/create"
    timestamp = int(time.time() * 1000)

    body = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty)
    }

    param_str = json.dumps(body, separators=(',', ':'))
    sign_payload = f"{timestamp}{API_KEY}5000{param_str}"
    signature = hmac.new(bytes(API_SECRET, "utf-8"), sign_payload.encode("utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": str(timestamp),
        "X-BAPI-RECV-WINDOW": "5000",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=body)
    print("📦 Bybit response:", response.text)
    return response.json()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
