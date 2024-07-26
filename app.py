from flask import Flask, request, jsonify, session, render_template, redirect, url_for, g
import sqlite3
import bcrypt
import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import re
import fitz

app = Flask(__name__)
app.secret_key = 'sk-proj-YaLgqvYmqPyynwwPQ6uyT3BlbkFJxRmMVVNUtIwauJBEwDIN'  # Replace with a secure key

# Initialize the language model
llm = ChatOpenAI(model="gpt-4")

# Define the rules and prompt template
rules_and_info = """
Rules: You are banking bot for Durham Bank and Your name is DB. And everything provided here is authenticated from bank
You can not assume anything on your own outside of these rules.
If you get input as chat sequence : Question:"", Response:"",Question:"", Response:"",Question:"", Response:"" ; in this case you just have to Answer the last asked question only and if it is out of the scope of rules_and_info, just say I can not respond to that query.
1. Verify customer identity before providing any information related to any of their accounts, to verify mention their account number and name, is consent provided as yes then only provide the details.
2. Verify customer identity before making any changes to account status.
3. User data are confidential, You can not ask who the user is or provide any other information then asked. 
4. For all user queries you need to check database first , for example if someone wants to activate {service} then you need to check it if it is already active or not and then if not you must confirm what action you will be taking with the user and then you can activate or deactiavte.
5. Costumer Query : Want to know how to download the statement. Answer: "Statement.pdf", do not add any other words.
6. Costumer Query : Wants to know about how to get personal loan. Answer : "P_loan.pdf" , do not add any other words.
7. Costumer Query : Wants to know about how to get Home loan. Answer : "H_loan.pdf" , do not add any other words.
8. Costumer Query : Wants to know about how to get any type of vehicle loan. Answer : "A_loan.pdf" , do not add any other words.
9. If costumer doesn't mention which loan he or she requires , ask them.
10. do not respond to the query directly if "what loans are active on my account" is asked. Answer: Provide with you User Name and Customer Id.
11. Costumer Query: Login related question. Answer: L_ogin.pdf
12. when user uses language other than English , You must response in their language.
13. Do sentiment analysis based on user input and if sound angry or disappointed or you can not solve problem at all, transer to the agent
"""

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, SQL result, and additional rules and information, answer the user question.
        You are performing sql query inside python environment, so write clean queries.
        for example: 
        SELECT balance FROM accounts WHERE account_type = 'Checking' AND customer_name = 'John Doe';
        SELECT date, amount, transaction_type FROM transactions
        WHERE account_id = (SELECT account_id FROM accounts WHERE account_type = 'Checking' AND customer_name = 'John Doe')
        ORDER BY date DESC LIMIT 1;
        SELECT loan_type, amount, status FROM loans
        WHERE account_id IN (SELECT account_id FROM accounts WHERE customer_name = 'John Doe');
        SELECT amount FROM loans
        WHERE loan_type = 'Home' AND account_id IN (SELECT account_id FROM accounts WHERE customer_name = 'John Doe');
        SELECT amount FROM loans WHERE loan_id = 1;

Rules and Information: {rules}
Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(session['customer_db'])
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def authenticate_user(username, password):
    login_db = sqlite3.connect('login.db')
    cursor = login_db.cursor()
    cursor.execute('SELECT password, database FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        login_db.close()
        return result[1]  # Return the database name
    else:
        login_db.close()
        return None

def extract_and_read_pdf(response):
    match = re.search(r'(\w+_\w+)\.pdf', response)
    if match:
        pdf_name = match.group(1)
        pdf_path = f'{pdf_name}.pdf'
        if not os.path.exists(pdf_path):
            return f"I cannot answer that currently. I am still learning."
        try:
            doc = fitz.open(pdf_path)
            text = ''
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            return f"Error providing answer: {e}"
    else:
        return response

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    username = data['username']
    password = data['password']
    customer_db = authenticate_user(username, password)
    if customer_db:
        session['username'] = username
        session['customer_db'] = customer_db
        return jsonify({'status': 'success', 'database': customer_db})
    else:
        return jsonify({'status': 'failure'})

@app.route('/query', methods=['POST'])
def query():
    if 'username' not in session:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'})
    data = request.json
    question = data['question']
    customer_db = session['customer_db']
    db = SQLDatabase.from_uri(f"sqlite:///{customer_db}")
    write_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)
    
    final_chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )
    
    response = final_chain.invoke({'question': question, 'rules': rules_and_info})
    print(f"Response: {response}")
    final_response = extract_and_read_pdf(response)
    print(f"Final Response: {final_response}")
    return jsonify({'response': final_response})

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == '__main__':
    app.run(debug=True)
