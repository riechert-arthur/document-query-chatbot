import streamlit

import extra_streamlit_components as stx

from login import register_user, login_user
from database_manager import DatabaseManager
from password import hash_password
from openai_manager import get_threads, create_thread
from thread_manager import ThreadManager

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

    if not "chat" in streamlit.session_state:
        streamlit.session_state["chat"] = user["chat_history"]

    with streamlit.container():

        chat_history = streamlit.session_state["chat"]

        with streamlit.chat_message(name="assistant", avatar="🤖"):

            streamlit.write(f"Hello! How can I help you today, {streamlit.session_state["username"]}?")

        if chat_history:

            for message in chat_history:

                role = message["role"]

                with streamlit.chat_message(name=role, avatar="🤖" if role == "assistant" else "👨"):

                    streamlit.markdown(message["content"])

    if prompt := streamlit.chat_input(placeholder="Your message..."):

        chat_history = streamlit.session_state["chat"]

        with streamlit.chat_message(name="user", avatar="👨"):

            streamlit.write(prompt)
            chat_history.append({"role": "user", "content": prompt})

        with streamlit.spinner("Thinking..."):

            with streamlit.chat_message(name="assistant", avatar="🤖"):
                
                response = thread.get_response(prompt).data[0].content[0].text.value

                chat_history.append({"role": "assistant", "content": response})
                db.update_chat_history(streamlit.session_state["username"], chat_history)

                streamlit.markdown(response)

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
