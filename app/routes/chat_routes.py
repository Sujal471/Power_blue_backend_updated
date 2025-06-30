from flask import Blueprint, request, jsonify
import app.services.bot_backend as chat
import app.services.database_insert as prac

chat_bp = Blueprint("chat_bp", __name__)
rag_chain = chat.rag_chain

@chat_bp.route("/", methods=["POST"])
def chat_route():
    data = request.json
    phone_no = data.get("phone_no")
    question = data.get("message")
    name = data.get("name")

    chat_history = prac.retrieve_chat_history(phone_no)
    ai_response_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})

    prac.store_chat(
        phone_no=phone_no,
        name=name,
        user_question=question,
        ai_response=ai_response_1["answer"]
    )

    return jsonify({"response": ai_response_1["answer"]})
