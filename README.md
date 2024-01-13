# Personal Streamlit Chatbot
A chatbot that utilizes OpenAI's assistants API to allow users to hold conversations, and
have their history persisted across sessions using MongoDB.

Users can create an account, and the app will use database queries to track their conversation history,
and user accounts will be deleted once they reach the word limit (for demo purposes only).

## How to Use
1. Make a clone of the repository.
2. In the `src` folder, make sure to change the `.streamlit_example` folder to `.streamlit`.
3. Go to `.streamlit/secrets.toml`, and change the placeholders after creating the corresponding accounts.
4. Open a terminal in the root directory, and run:
    ```
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```
5. Open a terminal in the `src` folder, and run `streamlit run main.py`.
6. The context limit is hard-coded in `Login.py` and can be changed there. In addition, the name of the collection/database is hard-coded in database_manager.py, and should be changed there.

## Technologies
- Python
- Streamlit
- GPT-4
- MongoDB
