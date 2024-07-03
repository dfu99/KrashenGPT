from app import app
from flask import session, request, jsonify
from app import gpt
import json


@app.route("/sendAnswer", methods = ['POST'])
def sendAnswer():
    target_text = session['target_text']
    user_text = request.json['text']
    language = session['LANGUAGE']
    # Process the correctness of the translation
    print("Comparing {} and {}".format(target_text, user_text))
    if gpt.check_correctness(target_text, user_text, language):
        response = 1
    else:
        response = 0
    return jsonify({'response': response})