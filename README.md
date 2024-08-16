Here’s a basic structure for a README file for your Flask banking application, integrating LangChain and SQL queries:

---

# Flask Banking Chatbot Application

This is a Flask-based banking chatbot application designed for Durham Bank. It uses LangChain to process user queries, execute SQL commands, and return appropriate responses based on predefined rules. The chatbot handles various banking operations and queries, including money transfers, credit card payments, and loan management.

## Features

- **User Authentication**: Secure login with hashed password verification.
- **Dynamic Query Handling**: Translates user queries into SQL commands using LangChain.
- **PDF Responses**: Provides responses in PDF format based on predefined rules.
- **Transaction Management**: Supports money transfers between accounts, credit card payments, and loan EMI payments.
- **PDF Reading**: Extracts and reads information from PDF files.

## Installation

### Prerequisites

- Python 3.8+
- Flask
- SQLite
- LangChain
- Other Python libraries

### Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/banking-chatbot.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd banking-chatbot
   ```

3. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Set Up Environment Variables**

   Create a `.env` file in the project root and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

7. **Create the SQLite Database**

   - Make sure you have a `login.db` and `customer_db` for authentication and customer data.

8. **Run the Application**

   ```bash
   flask run
   ```

## Configuration

- **`app.py`**: Main Flask application file where routes and functionality are defined.
- **`models.py`**: Contains database models and SQLAlchemy setup.
- **`config.py`**: Configuration settings for the application.
- **`rules_and_info`**: Contains the rules and information for processing user queries.

## Usage

1. **Login**: Users must log in with their username and password.
2. **Chat**: Interact with the chatbot to perform various banking tasks. The bot translates user queries into SQL commands and retrieves the necessary information.
3. **PDF Responses**: For certain queries, the bot will respond with a link to a PDF document.

## Troubleshooting

- Ensure that the `.env` file is properly set up with your API key.
- Verify that the SQLite database files are correctly configured and located in the project directory.
- Check the application logs for any errors during execution.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements or bug fixes.



---
