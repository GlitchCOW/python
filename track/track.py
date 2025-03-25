from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Enable CORS for frontend usage
from flask_cors import CORS
CORS(app)

def get_ip_location(ip=None):
    """Fetch location details for a given IP (or current user's IP)."""
    try:
        # If no IP is provided, use the requester's IP
        url = f"https://ipinfo.io/{ip}/json" if ip else "https://ipinfo.io/json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        return {
            "ip": data.get("ip", "Unknown"),
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country", "Unknown"),
            "coordinates": data.get("loc", "Unknown"),
            "org": data.get("org", "Unknown"),  # ISP / Organization
            "timezone": data.get("timezone", "Unknown"),
        }

    except requests.RequestException as e:
        return {"error": str(e)}

@app.route("/get-location", methods=["GET"])
def get_location():
    """API endpoint to return location details in JSON format."""
    ip = request.args.get("ip")  # Optional IP lookup
    data = get_ip_location(ip)
    return jsonify(data)

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)

    

