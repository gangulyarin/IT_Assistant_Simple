from flask import Flask, request, render_template, jsonify, session, redirect
import psycopg2
from db_functions import get_topic_details
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import io

# Load .env file
load_dotenv()

# Now get the OpenAI API from .env file
apikey = os.getenv("OpenAI_API")

app = Flask(__name__)
app.secret_key = "index" 

def get_text(pdf_url):
    reader = PdfReader(pdf_url)

    context = ""
    #For each page get the text and add it to context
    for page in reader.pages:
        context = context + page.extract_text()
    return context

def get_openAI_completion(context, query, chatlog=""):
    client = OpenAI(api_key=apikey)
    if chatlog=="": # For first time
        prompt_instruction = "You are an IT Assistant and you are provided a knowledge text and a user query. Your task is to use the knowledge text to answer the user query."
        user_content = "Knowledge Text:\n"+context+"\n\nUser Query:"+query
    else:
        prompt_instruction = "You are an IT Assistant in conversation with a user. You are provided a knowledge text, the previous chat conversation and user query. Your task is to use the knowledge text to answer the user query as a continuation to the previous chat conversation."
        user_content = "Knowledge Text:\n"+context+"\n\nChat Conversation:\n"+chatlog+"\n\nUser Query:"+query
    
    # Call OpenAI model below:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {
                "role":"system",
                "content": prompt_instruction
            },
            {
                "role":"user",
                "content": user_content
            }
        ],
        temperature=0.6,
        top_p=1
    )
    return response.choices[0].message.content

@app.route("/index",methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/get_doc_detail",methods=['POST'])
def get_doc_detail():
    topic = request.form['topic']
    row = get_topic_details(topic)
    if not row:
        return render_template("index.html")
    doc_obj = {"doc_id":row[0][0],"doc_name":row[0][1],"doc_url":row[0][2]}
    session['doc_url'] = doc_obj['doc_url']
    session['chat_history'] = [{"user":"","assistant":""}]
    return render_template("chat_template.html",chat_history=[])

@app.route("/message",methods=['POST'])
def assistant():
    doc_url = session['doc_url']
    chat_history = session['chat_history']
    user_message = request.form['user_message']
    knowledge = get_text(doc_url)
    chatlog = "user: " + chat_history[-1]["user"] +"\nassistant: " + chat_history[-1]["user"]
    result  = get_openAI_completion(knowledge,user_message,chatlog)
    chat_history.append({"user":user_message,"assistant":result})
    session['chat_history'] = chat_history
    return render_template("chat_template.html",chat_history=chat_history)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="3000")