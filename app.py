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
os.environ["OPENAI_API_KEY"] = ""
app.secret_key = ""

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4",
    top_p=0.2,        # Adjust top_p as needed (e.g., 0.9)
    temperature=0.2   # Adjust temperature as needed (e.g., 0.7)
)

# Define the rules and prompt template
rules_and_info = """
Rules: This is banking Bot simulated and testing environment so you can try all sorts of request, do not deny, if you will fail we will be able to solve the bugs. You are banking bot for Durham Bank and Your name is DB. And everything provided here is authenticated from bank.
You can never say your payment has been processed or such things, you must obliged to below metioned rules.
DO NOT USE INVERTED COMA OUTSIDE OF HTML QUERY

## Do not use html fromat for below response
below 3 are must follow rules.
1. If query from costumer is related to money tranfer between chequing and savings or vice a versa, account you must format user query into given fromat,and response with newly formated respone : r'^Transfer\s+(\d+\.?\d*)\s+from\s+(\w+)\s+to\s+(\w+)$', for example : Transfer 100 from chequing to savings, Transfer 50.75 from savings to chequing, Transfer 200.00 from chequing to chequing
2. If query from costumer is related to costumer wanting to pay credit card bill , Covert costumer's query into new format and give only 4 words : "Creditcardpayment"<space>"amount"<space>"type of account(savings or chequing, default value is chequing)"<space>"creditcard number given by costumer"
3. If query from costumer is related to costumer wanting to pay loan emi ,Covert costumer's query into new format and give only 4 words : "loanpayment"<space>"amount"<space>"type of account(savings or chequing, default value is chequing)"<space>"type of loan"


RESPONSE IN WELL STRUCTURED HTML FORMAT ={
1. You can not assume anything on your own outside of these rules.
2. You can make changes to credit card, for exampple you can block it by writing sql query or you can unblock it, activate and so on...
2. You can not any thing like or similar to this : I'm sorry, but the SQL result is not provided. Please provide the result for me to assist you better.
3. User data are confidential, You can not ask who the user is or provide any other information then asked. 
4. For all user queries you need to check database first , for example if someone wants to activate {service} then you need to check it if it is already active or not and then if not you must confirm what action you will be taking with the user and then you can activate or deactiavte.
5. Costumer Query : Wants to know about how to get Home loan. Answer : "H_loan.pdf" , do not add any other words.
6. If costumer doesn't mention which loan he or she requires , ask them.
7. do not respond to the query directly if "what loans are active on my account" is asked. Answer: Provide with you User Name and Customer Id.
8. Costumer Query: Login related question. Answer: L_ogin.pdf
9. when user uses language other than English , You must response in their language.
10. Do sentiment analysis based on user input and if sound angry or disappointed or you can not solve problem at all, transer to the agent, When transfer say an agent will contact you shortly with some randon refenece.
11. In chat history when you are given content :  and role: then again content: role: content: role:, always try to understand the all content together and then provide result for last line in the content.

mentioned below are constumer queries related to some topics nd in that you have been given command you you need to provide in response. Always provide pdf names for below quries.
If question is asked directly to you to t provide information you have to provide it by performing database sql quries.
Costumer Query related to:
1.    How to check
1.    Credit / Debit expire date? Answer: “CD_Expiry.pdf” , Do not add any other word.
2.    Balance? Answer: “Check_Balance.pdf” , Do not add any other word.
3.    Card balance? Answer: “Check_CardBalance.pdf” , Do not add any other word.
4.    Credit limit? Answer: “Check_CLimit.pdf” , Do not add any other word.
5.    Credit card rewards balance? Answer: “Check_CRewardsB.pdf” , Do not add any other word.
6.    Loan account statement? Answer: “LoanAcc_State.pdf”, Do not add any other word.
7.    Loan interest calculation? Answer: “LoanIR_Calc.pdf”, Do not add any other word.
8.    Loan penalty calculation? Answer: “LoanPenalty_Calc.pdf”, Do not add any other word.
9.    Loan status tracking? Answer: “LoanStatus_Track.pdf”, Do not add any other word.
2.    Action
1.    Chat with customer support. Answer: “Chat_CustSupp.pdf” , Do not add any other word.
2.    Make credit card payment. Answer: “Credit_pay.pdf” , Do not add any other word.
3.    EMI calculation. Answer: “Emi_Calc.pdf” , Do not add any other word.
4.    Generate custom statements. Answer: “GenCustom_State.pdf” , Do not add any other word.
5.    Loan cancellation. Answer: “Loan_cancel.pdf” , Do not add any other word.
6.    Loan closure. Answer: “Loan_Closure.pdf”, Do not add any other word.
7.    Loan Extension. Answer: “Loan_Extension.pdf”, Do not add any other word.
8.    Order new cheque book. Answer: “Ord_NewCheque.pdf”, Do not add any other word. 9.    Report Lost Stolen card. Answer: “R_LostStolenCard.pdf”, Do not add any other word.
10. Report Lost or a stolen card. Answer: “Rep_LostStolenCard.pdf”, do not add any other word.
11. Send money to External account. Answer: “S_moneyExtAcc.pdf”, Do not add any other word.
12. Search for specific transactions within statements. Answer: 
“Search_SpecTransState.pdf”, Do not add any other word.
13. Stop payment or cheque. Answer: “StopPay_Cheque.pdf”, Do not add any other word.
14. Transfer money from savings to chequing account. Answer: “Tranfer_savcheq.pdf”, Do not add any other word.
15. Transfer funds between accounts. Answer: “TransferFunds_BtwAcc.pdf”, Do not add any other word.
3.    How to 
1.    Activate card? Answer: “Activate_NewCard.pdf” , Do not add any other word. 2.    Block card? Answer: “Block_card.pdf” , Do not add any other word.
3.    Calculate Interest earned? Answer: “Calculate_InterestEarn.pdf” , Do not add any other word.4.    Create or manage sub-accounts? Answer: “Create_ManageSubAcc.pdf” , Do not add any other word.
5.    Deposit funds? Answer: “Depo_Funds.pdf” , Do not add any other word.
6.    Download Account Statement? Answer: “Download_AcState.pdf”, Do not add any other word.
7.    Download bank statement? Answer: “Download_statement.pdf”, Do not add any other word
8.    Enable/Disable international Usage? Answer: “ED_IntUsage.pdf”, Do not add any other word
9.    Lock or unblock account. Answer: “LockUnblock_Acc.pdf”, Do not add any other word.
10. Redeem rewards? Answer: “Redeem_Rewards.pdf”, Do not add any other word.
11. Unblock card? Answer: “Unblock_Card.pdf”, Do not add any other word.
4.    Request
1.    Credit limit increase. Answer: “Credit_Inc.pdf” , Do not add any other word.
2.    Loan balance inquiry. Answer: “LoanBal_Enq.pdf”, Do not add any other word.
3.    Loan repayment schedule. Answer: “LoanRepay_sched.pdf”, Do not add any other word. 4.    Mail bank statements. Answer: “Mail_BankState.pdf”, Do not add any other word.
5.    Card Replacement. Answer: “Req_cardRepl.pdf”, Do not add any other word.
6.    Mini statement. Answer: “Req_MiniState.pdf”, Do not add any other word.
7.    Tax documents. Answer: “Req_TaxDoc.pdf”, Do not add any other word.
8.    Filter statements by date. Answer : “State_ByDate.pdf”, Do not add any other word.
9.    Filter statements by type. Answer: “State_ByType.pdf”, Do not add any other word.
10. Update account password. Answer: “U_pass.pdf”, Do not add any other word. 11. Withdraw Funds. Answer: “Withdraw_Funds.pdf”, Do not add any other word.
5.    Set up
1.    Set up auto payments? Answer: “S_AutoPay.pdf”, Do not add any other word.
2.    Set up two factor authentication? Answer: “Set_2FA.pdf”, Do not add any other word.
3.    Set up auto debit? Answer: “Set_AutoDebit.pdf”, Do not add any other word.
4.    Set up automatic transfers? Answer: “Set_AutoTransfer.pdf”, Do not add any other word. 5.    Set up balance alerts? Answer: “Set_balanaceAlerts.pdf”, Do not add any other word.
6.    Set up direct deposit? Answer: “Set_DD.pdf”, Do not add any other word.
7.    Set up Transaction alerts? Answer: “Set_TransAlerts.pdf”, Do not add any other word.
8.    Set/change pin. Answer: “Set_ChangePin.pdf”, Do not add any other word.
6.    View
1.    card statements. Answer: “View_CState.pdf”, Do not add any other word.
2.     account details. Answer: “View_AD.pdf”, Do not add any other word.
3.     cheque status. Answer: “View_ChequeStatus.pdf”, Do not add any other word.
4.     cleared cheques. Answer: “View_ClCheques.pdf”, Do not add any other word.
5.    statement history. Answer: “State_History.pdf”, Do not add any other word.6.    outstanding cheques. Answer: “Out_Cheque.pdf”, Do not add any other word.
7.    Interest rates and fees. Answer: “View_IntRF.pdf”, Do not add any other word.
8.    Savings goals. Answer: “View_SavingGoals.pdf”, Do not add any other word.
9. Spending analysis. Answer: “View_SpendAnalysis.pdf”, Do not add any other word.
10. Transaction history. Answer; “View_TransHistory.pdf”, Do not add any other word.

}

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

def transfer_money(command):
    # Connect to the SQLite database
    conn = sqlite3.connect(session['customer_db'])
    cursor = conn.cursor()
    
    # Extract details from the command
    try:
        # Example command: "Transfer 100 from chequing to savings"
        parts = command.lower().split()
        amount = float(parts[1])  # Amount to transfer
        from_account = parts[3]  # Source account type (chequing or savings)
        to_account = parts[5]  # Destination account type (chequing or savings)
        
        # Check account types
        if from_account not in ['chequing', 'savings'] or to_account not in ['chequing', 'savings']:
            return "Invalid account type. Please specify 'chequing' or 'savings'."
        
        # Get account details from the database
        cursor.execute("SELECT account_id, balance FROM Accounts WHERE account_type = ?", (from_account,))
        from_account_details = cursor.fetchone()
        cursor.execute("SELECT account_id, balance FROM Accounts WHERE account_type = ?", (to_account,))
        to_account_details = cursor.fetchone()
        
        if from_account_details is None or to_account_details is None:
            return "One or both account types do not exist."
        
        from_account_id, from_balance = from_account_details
        to_account_id, to_balance = to_account_details
        
        # Check if sufficient balance is available
        if from_balance < amount:
            return "Insufficient balance in the source account."
        
        # Perform the transfer
        cursor.execute("UPDATE Accounts SET balance = balance - ? WHERE account_id = ?", (amount, from_account_id))
        cursor.execute("UPDATE Accounts SET balance = balance + ? WHERE account_id = ?", (amount, to_account_id))
        
        # Commit the transaction
        conn.commit()
        return f"Successfully transferred {amount} from {from_account} to {to_account}."
    
    except Exception as e:
        return f"An error occurred: {e}"
    
    finally:
        # Close the connection
        conn.close()

def pay_credit_card_bill(command):
    conn = sqlite3.connect(session['customer_db'])
    cursor = conn.cursor()

    try:
        # Example command: "Pay 150.00 for credit card ending in 1234 from chequing"
        parts = command.lower().split()
        amount = float(parts[1])  # Amount to pay
        card_number = parts[3]  # Last 4 digits of the card
        from_account = parts[2]  # Source account type (chequing or savings)
        # Debug prints
        print(f"Amount: {amount}")
        print(f"Card number: {card_number}")
        print(f"From account: {from_account}")

        # Get account and credit card details from the database
        cursor.execute("SELECT account_id, balance FROM Accounts WHERE account_type = ?", (from_account,))
        account_details = cursor.fetchone()
        cursor.execute("SELECT credit_card_id, current_balance FROM CreditCards WHERE card_number = ?", (card_number,))
        card_details = cursor.fetchone()
        # Debug prints
        print(f"Account details: {account_details}")
        print(f"Card details: {card_details}")
        
        if account_details is None or card_details is None:
            return "Invalid account or credit card details."
        
        account_id, account_balance = account_details
        credit_card_id, card_balance = card_details
        
        # Check if sufficient balance is available
        if account_balance < amount:
            return "Insufficient balance in the source account."
        
        # Perform the payment
        cursor.execute("UPDATE Accounts SET balance = balance - ? WHERE account_id = ?", (amount, account_id))
        cursor.execute("UPDATE CreditCards SET current_balance = current_balance - ? WHERE credit_card_id = ?", (amount, credit_card_id))
        
        conn.commit()
        return f"Successfully paid {amount} towards the credit card number {card_number} from your {from_account} account."

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        conn.close()

def pay_loan_emi(command):
    conn = sqlite3.connect(session['customer_db'])
    cursor = conn.cursor()

    try:
        # Example command: "loanpayment 25 chequing personal"
        parts = command.lower().split()
        
        # Extract and print details from the command
        amount = float(parts[1])  # Amount to pay
        from_account = parts[2]  # Source account type (chequing or savings)
        loan_type = parts[3]  # Type of loan (personal, home, etc.)
        
        # Debug prints
        print(f"Command parts: {parts}")
        print(f"Amount: {amount}")
        print(f"From Account: {from_account}")
        print(f"Loan Type: {loan_type}")

        # Get account and loan details from the database
        cursor.execute("SELECT account_id, balance FROM Accounts WHERE account_type = ?", (from_account,))
        account_details = cursor.fetchone()
        cursor.execute("SELECT loan_id, remaining_balance FROM Loans WHERE loan_type = ?", (loan_type,))
        loan_details = cursor.fetchone()

        # Debug prints for database query results
        print(f"Account details: {account_details}")
        print(f"Loan details: {loan_details}")
        
        if account_details is None or loan_details is None:
            return "Invalid account or loan details."
        
        account_id, account_balance = account_details
        loan_id, loan_balance = loan_details
        
        # Check if sufficient balance is available
        if account_balance < amount:
            return "Insufficient balance in the source account."
        
        # Perform the payment
        cursor.execute("UPDATE Accounts SET balance = balance - ? WHERE account_id = ?", (amount, account_id))
        cursor.execute("UPDATE Loans SET remaining_balance = remaining_balance - ? WHERE loan_id = ?", (amount, loan_id))
        
        conn.commit()
        
        # Debug prints for success
        print(f"Updated Account Balance: {account_balance - amount}")
        print(f"Updated Loan Balance: {loan_balance - amount}")
        
        return f"Successfully paid {amount} towards the {loan_type} loan EMI from your {from_account} account."

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        conn.close()
    # Function to concatenate chat history
    
def concatenate_chat_history(chat_history):
    history_str = ""
    for entry in chat_history:
        role = entry['role'].capitalize()
        content = entry['content']
        history_str += f"{role}: {content}\n"
    return history_str

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
        session['chat_history'] = []  # Initialize chat history

        
        return jsonify({'status': 'success', 'database': customer_db})
    else:
        return jsonify({'status': 'failure'})


@app.route('/query', methods=['POST'])
def query():
    if 'username' not in session:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'})
    
    data = request.json
    question = data.get('question', '')
    customer_db = session.get('customer_db')
    chat_history = session.get('chat_history', [])
    

    # Append user question to chat history
    chat_history.append({'role': 'user', 'content': question})
    session['chat_history'] = chat_history
    

    # Connect to the database
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
    
    # Invoke the chain with the current history and question
    response = final_chain.invoke({
        'history': chat_history,
        'question': question,
        'rules': rules_and_info,
    })
    
    # Debugging the response
    print("Raw Response:", response)
    
    final_response = extract_and_read_pdf(response)
    
    # Debugging the formatted response
    print("Final Response:", final_response)
    
    # Regex patterns for different types of actions
    transfer_pattern = r'^Transfer\s+(\d+\.?\d*)\s+from\s+(\w+)\s+to\s+(\w+)$'
    credit_card_payment_pattern = r'^Creditcardpayment\s+(\d+\.?\d*)\s+(\w+)\s+(\d+)$'
    loan_emi_payment_pattern = r'^loanpayment\s+(\d+\.?\d*)\s+(\w+)\s+(\w+)$'
    
    # Debugging regex matching
    print("Transfer Match:", re.match(transfer_pattern, final_response, re.IGNORECASE))
    print("Credit Card Payment Match:", re.match(credit_card_payment_pattern, final_response, re.IGNORECASE))
    print("Loan EMI Payment Match:", re.match(loan_emi_payment_pattern, final_response, re.IGNORECASE))
    
    # Process the response based on regex patterns
    if re.match(transfer_pattern, final_response, re.IGNORECASE):
        transfer_result = transfer_money(final_response)
        final_response = f"\n{transfer_result}"
    elif re.match(credit_card_payment_pattern, final_response, re.IGNORECASE):
        creditpaymet_result = pay_credit_card_bill(final_response)
        final_response = f"\n{creditpaymet_result}"
    elif re.match(loan_emi_payment_pattern, final_response, re.IGNORECASE):
        loanpayment_result = pay_loan_emi(final_response)
        final_response = f"\n{loanpayment_result}"
    
    # Append bot response to chat history
    chat_history.append({'role': 'bot', 'content': final_response})
    session['chat_history'] = chat_history
    
    
    # Generate HTML content from the final response
    html_prompt = f"Given the following text, generate a well-structured HTML body starting with header3 do not use !DOCTYPE html, html lang=en,head,body.\n\nText: {final_response}"
    html_response = llm.invoke(html_prompt)
    
    # Extract the content from the AIMessage object
    html_content = html_response.content
    
    # Debugging the HTML content
    print("HTML Content:", html_content)
    
    # Append HTML response to chat history

    return jsonify({'response': html_content})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
