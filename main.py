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
        data = request.get_json()
        print("📩 Webhook received:", data)

        if not data or 'symbol' not in data or 'side' not in data or 'qty' not in data:
            return jsonify({"error": "Invalid payload"}), 400

        symbol = data['symbol']
        side = data['side'].upper()
        qty = str(data['qty'])

        print(f"➡️ Order Info: {side} {qty} of {symbol}")

        # Step 2: Create order payload
        timestamp = str(int(time.time() * 1000))
        order_data = {
            "category": "spot",
            "symbol": symbol,
            "side": side,
            "orderType": "Market",
            "qty": qty,
            "timestamp": timestamp,
            "apiKey": API_KEY
        }

        # Step 3: Generate signature
        param_str = '&'.join([f"{key}={value}" for key, value in sorted(order_data.items())])
        signature = hmac.new(
            bytes(API_SECRET, "utf-8"),
            bytes(param_str, "utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-BYBIT-SIGN": signature
        }

        print("🔐 Signature:", signature)

        url = "https://api.bybit.com/spot/v3/private/order"
        response = requests.post(url, json=order_data, headers=headers)

        try:
            result = response.json()
        except ValueError:
            print("❌ Bybit returned non-JSON:", response.text)
            return jsonify({"error": "Invalid response from Bybit"}), 500

        print("📩 Response from Bybit:", result)

        if result.get("retCode") == 0:
            return jsonify({"message": "✅ Trade placed successfully"}), 200
        else:
            return jsonify({
                "error": result.get("retMsg", "Bybit API error")
            }), 400

    except Exception as e:
        print("❌ Error occurred:", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
