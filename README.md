# AI-Banking-chatbot
### Project Update Report: Real-Time Actionable Banking Chatbot (in progress project)

#### Objective
The aim of the project is to develop a banking chatbot capable of executing real-time actions such as blocking credit cards. This report provides an update on the progress, detailing the approaches tried, implementation environment, current status, and next steps.

---

#### Approaches

**1. LLM Model (Gemma)**
- **Custom Dataset**: We created a dataset tailored specifically to banking queries. This dataset includes various scenarios that customers might encounter, such as blocking a credit card, checking account balance, or requesting a new card.
- **Training Process**: The LLM (Gemma) model was fine-tuned using TensorFlow and PyTorch. This process involved adjusting the model parameters to better respond to specific banking queries.
- **Tools and Libraries**: TensorFlow and PyTorch were the primary libraries used for model training. Additional preprocessing tools were used to clean and prepare the dataset.
- **Performance**: The model was evaluated using metrics such as accuracy, precision, and recall. The fine-tuned model demonstrated high accuracy and relevance in its responses.
- **Outcome**: The successfully trained model delivers accurate and contextually appropriate responses to user queries, enhancing the chatbot's ability to handle banking tasks.

**2. LangChain and GPT API**
- **Chat Retrieval Chain**: Implemented a chat retrieval chain to fetch relevant information based on user inputs. This helps in understanding the context and retrieving the appropriate data.
- **Function Triggering**: Set up rules and conditions for triggering functions based on user queries. For example, when a user requests to block a credit card, the function triggering mechanism ensures the action is carried out seamlessly.
- **Tools and Libraries**: The OpenAI API and LangChain framework were used for implementing this approach. These tools help in creating robust and scalable solutions for handling user queries.
- **Capabilities**: Enabled the chatbot to perform actions like blocking credit cards, updating records, and providing real-time information.
- **Outcome**: Successfully integrated function triggering with chat responses, allowing the chatbot to perform actionable tasks based on user inputs.

---

#### Implementation Environment
- **Streamlit**: Used for creating the frontend interface, providing a chat-like environment for user interactions. Streamlit makes it easy to build and deploy interactive web applications.
- **Flask API**: Handles the backend logic, including data queries and interactions with the dataset. Flask provides a lightweight framework for building web applications and APIs.
- **Integration**: The Streamlit frontend communicates with the Flask backend, allowing for real-time data actions such as blocking credit cards. This integration ensures smooth and efficient handling of user requests.

---

#### Current Status and Testing
- **Testing Environment**: Final testing is being conducted in Jupyter Notebook. This environment allows for detailed analysis and debugging of the chatbot's performance.
- **Trial Mode**: Both approaches are currently in trial mode, allowing us to evaluate their effectiveness and identify areas for improvement.
- **Progress**: The testing phase has yielded positive results, with the chatbot successfully handling various banking queries. Some issues have been identified and are being addressed.
- **Next Steps**: Immediate tasks include final testing and debugging. We aim to resolve any outstanding issues to ensure the chatbot functions smoothly.

---

#### Next Steps
- **Immediate Tasks**: Complete final testing and debugging in Jupyter Notebook.
- **Integration**: Transition from trial mode to production. This involves making the necessary adjustments to ensure the chatbot is ready for deployment.
- **Deployment**: Deploy the chatbot on the banking platform, making it accessible to users.


---
