from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import os
import requests
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
        data = request.json
        print("Received alert:", data)

        symbol = data.get("symbol")
        side = data.get("action").upper()
        qty = data.get("qty", 10)

        if symbol and side in ["BUY", "SELL"]:
            result = place_order(symbol, side, qty)
            return jsonify(result), 200
        else:
            return jsonify({"error": "Invalid payload"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def place_order(symbol, side, qty):
    timestamp = int(time.time() * 1000)

    url = "https://api.bybit.com/v5/order/create"
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": str(timestamp),
        "X-BAPI-RECV-WINDOW": "5000",
        "Content-Type": "application/json"
    }

    body = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty)
    }

    # Create signature
    import json
    param_str = json.dumps(body, separators=(',', ':'))
    sign_payload = f"{timestamp}{API_KEY}5000{param_str}"
    signature = hmac.new(bytes(API_SECRET, "utf-8"), sign_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    headers["X-BAPI-SIGN"] = signature

    # Send request
    response = requests.post(url, headers=headers, json=body)
    print("Bybit response:", response.text)
    return response.json()

if __name__ == "__main__":
    app.run(debug=True)
