from flask import Blueprint, request, jsonify

on_server_bp = Blueprint("on_server_bp", __name__)

@on_server_bp.route("/", methods=["POST","GET"])
def on_server():
    return "Server is running"