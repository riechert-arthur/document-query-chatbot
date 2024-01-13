import streamlit

import extra_streamlit_components as stx

from login import register_user, login_user
from database_manager import DatabaseManager
from password import hash_password
from openai_manager import get_threads, create_thread
from thread_manager import ThreadManager

import time

"""
The main driver file to run streamlit.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

def page() -> None:
    streamlit.title("Chatbot Demo")

def authenticated() -> bool:
    if not streamlit.session_state["cookies"].get("logged_in"):
        
        return False

    else:

        return streamlit.session_state["cookies"].get("logged_in")["state"]
    


def login_page() -> str:

    with streamlit.form(key="login", border=True):
        
        streamlit.header("Login")
        
        username: str = streamlit.text_input("Username")
        password: str = streamlit.text_input("Password", type="password")

        if streamlit.form_submit_button("Login"):
            
            if not username or not password:

                streamlit.warning("You need a username and password!")

            else:

                with streamlit.spinner("Logging In..."):

                    db = DatabaseManager(streamlit.secrets["authentication"]["uri"])
                    
                    if login_user(
                        user=username,
                        password=password,
                        db=db,
                    ):

                        streamlit.success("You're logged in!")
                        streamlit.session_state["cookies"].set("logged_in", { "state": True, "username": username })
                        streamlit.rerun()
                    
                    else:

                        streamlit.warning("Incorrect credentials.")       

    if streamlit.button("Sign Up Instead"):
        streamlit.session_state["show_login"] = False
            

def signup_page() -> str:

    with streamlit.form(key="signup", border=True):

        streamlit.header("Sign Up")
        streamlit.subheader("Enter a basic username to keep track of chat history and retrieve your messages at any date.")

        username: str = streamlit.text_input("Username")
        password: str = streamlit.text_input("Password", type="password")

        if streamlit.form_submit_button("Sign Up"):

            if not username or not password:

                streamlit.warning("You need a username and password!")

            else:

                with streamlit.spinner("Registering..."):

                    db = DatabaseManager(streamlit.secrets["authentication"]["uri"])
                    success = register_user(
                        user=username,
                        hash=hash_password(password),
                        db=db
                    )

                    if not success:

                        streamlit.warning("User already exists! Try Again!")

                    else:

                        streamlit.success("You're registered!")
                        streamlit.session_state["show_login"] = True

    if streamlit.button("Log In Instead"):
        streamlit.session_state["show_login"] = True

def auth_page():

    if not "show_login" in streamlit.session_state:
        streamlit.session_state["show_login"] = True

    if streamlit.session_state["show_login"]:
        login_page()
    else:
        signup_page()

def chat(db: DatabaseManager):

    user = db.get_user(streamlit.session_state["username"])
    thread_id = ""

    if not user["threads"]:
        thread_id = create_thread(streamlit.secrets["openai"]["api_key"])
        db.add_thread(user["user"], thread_id)
    else:
        thread_id = user["threads"][0]

    thread = ThreadManager(
        api_key=streamlit.secrets["openai"]["api_key"],
        assistant_id=user["assistant_id"],
        thread_id=thread_id
    )

    with streamlit.container(border=True):

        with streamlit.chat_message(name="assistant", avatar="🤖"):

            streamlit.write(f"Hello! How can I help you today, {streamlit.session_state["username"]}?")

        for message in thread.get_all_messages().data:

            with streamlit.chat_message(name=message.role, avatar="🤖" if message.role == "assistant" else "👨"):

                streamlit.markdown(message.content[0].text.value)

    if prompt := streamlit.chat_input(placeholder="Your message..."):

        with streamlit.chat_message(name="user", avatar="👨"):

            streamlit.write(prompt)

        with streamlit.spinner("Thinking..."):

            with streamlit.chat_message(name="assistant", avatar="🤖"):
                
                streamlit.markdown(thread.get_response(prompt).data[0].content[0].text.value)

"""
TO BE REPLACED
"""
def chat_history(db: DatabaseManager):

    users = db.retrieve({"user": streamlit.session_state["username"]})
    thread_ids = []
    history = []
    previews = []

    for user in users:
        if user["user"] == streamlit.session_state["username"]:
            thread_ids = user[threads]

    threads = get_threads(
        api_key=streamlit.secrets["openai"]["api_key"],
        thread_ids=thread_ids
    )


if __name__ == "__main__":

    streamlit.session_state["cookies"] = stx.CookieManager()
    db = DatabaseManager(streamlit.secrets["authentication"]["uri"])

    if "thread" not in streamlit.session_state:
        streamlit.session_state["thread"] = 1
    
    if not authenticated():
        auth_page()
    else:
        streamlit.session_state["username"] = streamlit.session_state["cookies"].get("logged_in")["username"]
        chat(db)
