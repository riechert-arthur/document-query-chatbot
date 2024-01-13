import streamlit as st
from extra_streamlit_components import CookieManager

from utils.authentication_utils import register_user, login_user
from utils.password_utils import hash_password
from utils.openai_utils import create_thread, delete_assistant
from managers.database_manager import DatabaseManager
from managers.thread_manager import ThreadManager

import time
from typing import Set, Union

# Metadata
def configuration() -> None:
    st.set_page_config(
        page_title="Streamlit Chatbot Demo",
        page_icon="🤖",
    )

# The title and subheader
def header() -> None:
    st.title("Streamlit Chatbot Demo")
    st.subheader("By: Arthur Riechert")

# Whether or not the user is logged in.
def authenticated(cookie_manager) -> bool:
    if not cookie_manager.get("logged_in"):
        
        return False

    else:

        return cookie_manager.get("logged_in")["state"]
    
# Checks if the user has a thread
def thread_init() -> None:
    if "thread" not in st.session_state:
        st.session_state["thread"] = 1
    
# Creates the database instance
def database_init() -> DatabaseManager:

    uri: str = st.secrets["authentication"]["uri"]

    return DatabaseManager(uri)

# Creates cookie manager instance
def cookie_init() -> CookieManager:

    return CookieManager()

# Wipes all the user's data
def wipe_user(user: dict, db: DatabaseManager, cookie_manager: CookieManager) -> None:

    # Data needed to remove from openai platform
    openai_api_key: str = st.secrets["openai"]["api_key"]
    assistant_id: str = user["assistant_id"]

    delete_assistant(openai_api_key, assistant_id)

    user_id: str = user["_id"]
    db.delete_user(user_id)

    # Reset the cookies
    cookie_manager.delete("logged_in")
    
    updated_cookie: dict = { "state": False, "username": "" }
    cookie_manager.set("logged_in", updated_cookie)

    st.rerun()

def login_button(
    cookie_manager: CookieManager,
    db: DatabaseManager,
    username: str,
    password: str
) -> None:

    if st.form_submit_button("Login"):
            
        if not username or not password:

            st.warning("You need a username and password!")

        else:

            log_in_user(cookie_manager, db, username, password)    

# Performs authentiation
def log_in_user(
    cookie_manager: CookieManager,
    db: DatabaseManager,
    username: str,
    password: str
) -> None:
    with st.spinner("Logging In..."):

        db = DatabaseManager(st.secrets["authentication"]["uri"])
        
        if login_user(
            user=username,
            password=password,
            db=db,
        ):

            st.success("You're logged in!")
            cookie_manager.set("logged_in", { "state": True, "username": username })
            time.sleep(0.5)
            st.rerun()
        
        else:

            st.warning("Incorrect credentials.") 

# Assembles all login components
def login_page(db: DatabaseManager, cookie_manager: CookieManager) -> None:

    with st.form(key="login", border=True):
        
        st.header("Login")
        
        username: str = st.text_input("Username")
        password: str = st.text_input("Password", type="password")

        login_button(cookie_manager, db, username, password)

    if st.button("Sign Up Instead"):
        st.session_state["show_login"] = False

# Performs the process of signing up a user
def sign_up_user(db: DatabaseManager, username: str, password: str) -> None:
    with st.spinner("Registering..."):

        db = DatabaseManager(st.secrets["authentication"]["uri"])
        success = register_user(
            user=username,
            hash=hash_password(password),
            db=db
        )

        if not success:

            st.warning("User already exists! Try Again!")

        else:

            st.success("You're registered!")
            st.session_state["show_login"] = True
            time.sleep(0.5)
            st.rerun()

# The button to sign up
def signup_button(db: DatabaseManager, username: str, password: str) -> None:
    if st.form_submit_button("Sign Up"):

        if not username or not password:

            st.warning("You need a username and password!")

        else:

            sign_up_user(db, username, password) 

# Assembles signup components
def signup_page() -> str:

    with st.form(key="signup", border=True):

        st.header("Sign Up")
        st.subheader("Enter a basic username to keep track of chat history and retrieve your messages at any date.")

        username: str = st.text_input("Username")
        password: str = st.text_input("Password", type="password")

        signup_button(db, username, password)

    if st.button("Log In Instead"):
        st.session_state["show_login"] = True

# Assembles login and singup pages
def auth_page(db: DatabaseManager, cookie_manager: CookieManager):

    if not "show_login" in st.session_state:
        st.session_state["show_login"] = True

    if st.session_state["show_login"]:
        login_page(db, cookie_manager)
    else:
        signup_page()

# An introduction from the bot
def chat_introduction() -> None:

    with st.chat_message(name="assistant", avatar="🤖"):

        st.write(f"Hello! How can I help you today, {st.session_state["username"]}?")

# Assemble's user's previous messages.
def previous_messages() -> None:
    chat_history = st.session_state["chat"]

    if chat_history:

        for message in chat_history:

            role = message["role"]

            with st.chat_message(name=role, avatar="🤖" if role == "assistant" else "👨"):

                st.markdown(message["content"])


# Assembles introduction and user's previous messages.
def display_chat_history() -> None:

    with st.container():

        chat_introduction()
        previous_messages()

# Creates a new thread manager
def chat_init(db: DatabaseManager, cookie_manager: CookieManager) -> Set[Union[dict, ThreadManager]]:
    user = db.get_user(st.session_state["username"])
    thread_id = ""

    # Create thread if one doesn't exist.
    try:
        if not user["threads"]:
            thread_id = create_thread(st.secrets["openai"]["api_key"])
            db.add_thread(user["user"], thread_id)
        else:
            thread_id = user["threads"][0]

        thread = ThreadManager(
            api_key=st.secrets["openai"]["api_key"],
            assistant_id=user["assistant_id"],
            thread_id=thread_id
        )

        # Create session variable for chat history if it doesn't exist
        if not "chat" in st.session_state:
            st.session_state["chat"] = user["chat_history"]

        return user, thread

    # This occurs when the user runs out of words and has account reset.
    except Exception as e:

        st.warning("You have no more words remaining!")

        print(f"\033[31mError:\n{e.__traceback__}\033[0m")

# Detect if the user has gone over limit after receiving response
def check_assistant_response_length(
    db: DatabaseManager,
    cookie_manager: CookieManager,
    user: dict,
    remaining_words: int,
    response_length: int
) -> None:
    
    if remaining_words < response_length:
        with st.spinner("Terminating account; you've exceeded the word limit..."):
            wipe_user(user, db, cookie_manager)

# Display the assistant's response/
def assistant_response(
    db: DatabaseManager,
    cookie_manager: CookieManager,
    thread: ThreadManager,
    user: dict,
    prompt: str, 
    prompt_length: int,
    remaining_words: int,
    chat_history: list
) -> None:
    
    with st.spinner("Thinking..."):

        with st.chat_message(name="assistant", avatar="🤖"):
            
            response: str = thread.get_response(prompt).data[0].content[0].text.value
            response_length: int = len(response.split())
            remaining_words: int = remaining_words - response_length

            db.update_count(id=user["_id"], extra=prompt_length + response_length)

            chat_history.append({"role": "assistant", "content": response})
            db.update_chat_history(st.session_state["username"], chat_history)

            st.markdown(response)

            check_assistant_response_length(db, cookie_manager, user, remaining_words, response_length)

# Ensures that current prompt doesn't exceed length limit
def check_prompt_length(
    db: DatabaseManager,
    cookie_manager: CookieManager,
    user: dict,
    prompt_length: int,
    remaining_words: int
):
    if prompt_length > remaining_words:
        with st.spinner("Terminating account; you've exceeded the word limit..."):
            wipe_user(user, db, cookie_manager)

# The processing for the user's prompt.
def user_prompt(
    db: DatabaseManager,
    cookie_manager: CookieManager,
    user: dict,
    thread: ThreadManager
):
    if prompt := st.chat_input(placeholder="Your message..."):

        chat_history: list = st.session_state["chat"]
        prompt_length = len(prompt)
        remaining_words = user["limit"] - user["usage"]

        with st.chat_message(name="user", avatar="👨"):

            st.write(prompt)
            chat_history.append({"role": "user", "content": prompt})

        check_prompt_length(db, cookie_manager, user, prompt_length, remaining_words)

        assistant_response(db, cookie_manager, thread, user, prompt, prompt_length, remaining_words, chat_history)
        
# Assembles all chat elements
def chat(db: DatabaseManager, cookie_manager: CookieManager):

    user, thread = chat_init(db, cookie_manager)

    display_chat_history()

    user_prompt(db, cookie_manager, user, thread)
                        
    st.markdown(f"Current Usage:`{user["usage"]}`")

# A button that allows you to wipe all the user's data from the database
def wipe_button(db: DatabaseManager, cookie_manager: CookieManager) -> None:
    if st.button("Wipe Data"):
        user = db.get_user(st.session_state["username"])
        delete_assistant(st.secrets["openai"]["api_key"], user["assistant_id"])
        db.delete_user(user["_id"])
        cookie_manager.delete("logged_in")
        cookie_manager.set("logged_in", { "state": False, "username": "" })
        st.rerun()

# The side bar where some descriptions can be found.
def side_bar(db: DatabaseManager, cookie_manager: CookieManager) -> None:
    with st.sidebar:

        st.markdown("""
        # 💡Thanks for your time!
        ## This is a demo, and all accounts are limited to 3000 words sent and received.
        Once you have reached the limit, your account and all your chat history
        will automatically be wiped from the database, or you can **click
        the button below to completely wipe your data from the demo's
        database.**""")

        wipe_button(db, cookie_manager)

if __name__ == "__main__":

    configuration()
    header()

    thread_init()

    db: DatabaseManager = database_init()
    cookie_manager: CookieManager = cookie_init()
    
    if authenticated(cookie_manager) == False:
        auth_page(db, cookie_manager)
    else:
        st.session_state["username"] = cookie_manager.get("logged_in")["username"]
        chat(db, cookie_manager)
        side_bar(db, cookie_manager)