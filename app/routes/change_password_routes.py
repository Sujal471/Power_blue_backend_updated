from flask import Blueprint, request, jsonify
import requests
from app.services.User_login import verify_user, update_password
from app.config import Config

change_password_bp = Blueprint("change_password_bp", __name__)

@change_password_bp.route("/", methods=["POST"])
def change_password():
    data = request.get_json()

    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    recaptcha_token = data.get("recaptchaToken")

    # Validate input
    if not username or not old_password or not new_password or not recaptcha_token:
        return jsonify({"error": "All fields including captcha are required"}), 400

    # Step 1: Verify reCAPTCHA token with Google
    secret_key = Config.Google_Recaptcha
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": secret_key,
        "response": recaptcha_token
    }

    response = requests.post(verify_url, data=payload)
    result = response.json()

    if not result.get("success"):
        return jsonify({"error": "Failed CAPTCHA verification"}), 403

    # Step 2: Verify user
    if not verify_user(username, old_password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Step 3: Update password
    update_password(username, new_password)
    return jsonify({"message": "Password updated successfully"}), 200
