import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = "licenses.json"

# Load existing license data
try:
    with open(DATA_FILE, "r") as file:
        licenses = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    licenses = []

# Save changes to JSON file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(licenses, file, indent=4)

@app.route('/activate', methods=['POST'])
def activate_license():
    data = request.json
    mac_address = data.get("mac_address")
    license_key = data.get("license_key")

    if not mac_address or not license_key:
        return jsonify({"status": "error", "message": "MAC address and license key required"}), 400

    #Check if license exists in JSON
    for license_entry in licenses:
        if license_entry["LicenseKey"] == license_key:
            if license_entry["SetupDone"] == "YES":
                return jsonify({"status": "error", "message": "License already activated"}), 400
            
            #  Activate the license
            license_entry["MACKey"] = mac_address
            license_entry["SetupDone"] = "YES"
            license_entry["Status"] = "Active"
            save_data()
            return jsonify({"status": "success", "message": "License activated successfully"}), 200

    return jsonify({"status": "error", "message": "Invalid license key"}), 404

@app.route('/validate', methods=['POST'])
def validate_license():
    data = request.json
    mac_address = data.get("mac_address")
    license_key = data.get("license_key")

    #  Check if MAC matches the stored license
    for license_entry in licenses:
        if license_entry["LicenseKey"] == license_key:
            if license_entry["MACKey"] == mac_address and license_entry["SetupDone"] == "YES" and license_entry["Status"] == "Active":
                return jsonify({"status": "valid", "message": "License valid"}), 200
            elif license_entry["MACKey"] != mac_address and license_entry["SetupDone"] == "YES" and license_entry["Status"] == "Active":
                return jsonify({"status": "valid", "message": "License Invalid. Please contact Administrator"}), 800
            elif license_entry["MACKey"] != mac_address and license_entry["SetupDone"] == "NO" and license_entry["Status"] == "Not Active":
                return jsonify({"status": "invalid", "message": "MAC address not Found"}), 801
            return jsonify({"status": "invalid", "message": "MAC address not Found"}), 403

    return jsonify({"status": "invalid", "message": "License key not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)