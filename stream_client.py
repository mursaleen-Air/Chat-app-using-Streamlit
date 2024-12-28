import threading
import socket
import sys
import time
import streamlit as st
import time
import random
# Streamlit configuration
st.set_page_config(page_title="Chatroom", layout="wide")

# Global state for storing messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to update chat messages
def update_messages(new_messages):
    st.session_state.messages.extend(new_messages)

# Thread for receiving messages
class ReceiveThread(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message:
                    st.session_state.messages.append(message)
                    st.experimental_rerun()  # Refresh the Streamlit app to display new messages
            except (ConnectionResetError, ConnectionAbortedError):
                st.session_state.messages.append("Disconnected from server.")
                break

# Main client class
class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.1)  # Non-blocking with a timeout
        self.name = None

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            st.session_state.messages.append(f"Error connecting to server: {e}")
            return False

    def start(self, name):
        self.name = name
        self.sock.sendall(f"server: {self.name} has joined the chat.".encode('ascii'))
        st.session_state.messages.append(f"You joined as {self.name}. Type 'QUIT' to leave.")

    def receive_message(self):
        try:
            message = self.sock.recv(1024).decode('ascii')
            return message
        except socket.timeout:
            return None  # No new messages
        except Exception as e:
            return f"Error: {e}"

    def send_message(self, message):
        try:
            self.sock.sendall(message.encode('ascii'))
        except Exception as e:
            st.session_state.messages.append(f"Error sending message: {e}")


# Streamlit UI
import streamlit as st
import time
from datetime import datetime
import base64

st.markdown(
    """
    <style>
        body {
            background: linear-gradient(to right, #6a11cb, #2575fc); 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Image file not found: {image_path}")
        return None

# Path to the background image
image_path = "Picture/Capture.JPG"

# Get Base64 encoding of the image
base64_image = get_base64_image(image_path)
# Function to load the image and encode it to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image

# Path to your image
image_path = "Picture/Capture.JPG"
base64_image = get_base64_image(image_path)
users = {
    "1": "1",
    "2": "2",
    "3": "3"
}

# State variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False  # Whether the user is logged in
if "current_user" not in st.session_state:
    st.session_state.current_user = None  # Store the logged-in username

def main():
    # Initialize session state variables
    if "client" not in st.session_state:
        st.session_state.client = None

    if "messages" not in st.session_state:
        st.session_state.messages = []  # Stores messages as tuples: (timestamp, username, message)

    if "last_fetch" not in st.session_state:
        st.session_state.last_fetch = time.time()

    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0  # Track refresh button clicks

    st.title("Chatroom Client")
    st.sidebar.title("Connection Settings")



    
    if not st.session_state.logged_in:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.client = Client("127.0.0.1", 5050)  # Replace with your server's host and port
                if st.session_state.client.connect():
                    st.success(f"Logged in as {username}")
                else:
                    st.session_state.client = None  # Reset client if connection fails
                    st.error("Failed to connect to the server.")
            else:
                st.error("Invalid username or password")

    # Sidebar inputs for server details
    host = st.sidebar.text_input("Server Host", value="127.0.0.1")
    port = st.sidebar.number_input("Server Port", value=1060, step=1, format="%d")
    #name = st.sidebar.text_input("Your Name", value="")

    # Connect to the server
    # if st.sidebar.button("Connect") and not st.session_state.client:
    #     client = Client(host, port)
    #     if client.connect():
    #         client.start(name)
    #         st.session_state.client = client
    #         st.session_state.messages.append(
    #             (datetime.now().strftime("%H:%M:%S"), "System", f"Connected to {host}:{port} as {name}")
    #       )

    # Poll for new messages
# Divider for better organization in the sidebar
    st.sidebar.markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)

    # Add "Add New User" link styled as a button
    st.sidebar.markdown(
        """
        <a href="http://localhost:8501/" target="_blank" style="text-decoration:none;">
            <button style="padding:10px 20px; background-color:#007bff; color:white; border:none; border-radius:5px; cursor:pointer; width:100%;">
                Add New User
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )
    if base64_image:
        st.markdown(
            f"""
            <style>
                body {{
                    background-image: url("data:image/jpeg;base64,{base64_image}");
                    background-size: cover;
                    background-position: center;
                }}
                .stButton>button {{
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                }}
                .stButton>button:hover {{
                    background-color: #0056b3;
                }}
                .stTextInput>div>input {{
                    font-size: 14px;
                    padding: 5px;
                    width: 200px;
                }}
                .center-container {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 80vh;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Background image not applied due to missing file.")



    if st.session_state.client:
        current_time = time.time()
        if current_time - st.session_state.last_fetch > 0.5:  # Poll every 0.5 seconds
            new_message = st.session_state.client.receive_message()
            if new_message:
                # Assume server sends messages in format: "username: message"
                if ": " in new_message:
                    username, message = new_message.split(": ", 1)
                    st.session_state.messages.append((datetime.now().strftime("%H:%M:%S"), username, message))
                else:
                    st.session_state.messages.append((datetime.now().strftime("%H:%M:%S"), "Unknown", new_message))
            st.session_state.last_fetch = current_time


    # if st.session_state.logged_in:
    #     st.write(f"Welcome, {st.session_state.current_user}!")

    #     # Add the rest of your chatroom code here
    #     st.write("Chat messages will go here.")




    #     # Styled message container
    #     st.write("### Messages:")
    #     message_container = st.empty()
    #     with message_container:
    #         # Start the container div
    #         messages_html = (
    #             f"<div style='height:400px; overflow-y:auto; padding:10px; border:1px solid #ddd; background-color:#e0ffff; border-radius: 5px;'>"
    #         )
    #         for msg in st.session_state.messages:
    #             if len(msg) == 3:  # Ensure message has the expected format
    #                 timestamp, username, message = msg
    #                 user_color = hash(username) % 360  # Generate a unique color for each username
                    
    #                 # Add each message to the container
    #                 messages_html += (
    #                     f"<p style='margin:5px 0;'>"
    #                     f"<span style='color:gray;'>[{timestamp}]</span> "
    #                     f"<span style='color:hsl({user_color}, 70%, 50%); font-weight:bold;'>{username}:</span> "
    #                     f"{message}"
    #                     f"</p>"
    #                 )
    #         # Close the container div
    #         messages_html += "</div>"

    #         # Render the entire HTML content
    #         st.markdown(messages_html, unsafe_allow_html=True)



        # Input box and buttons at the bottom of the page
    # Input box and buttons at the bottom of the page
        # if st.session_state.client:
        #     if "current_input" not in st.session_state:
        #         st.session_state.current_input = ""

        #     st.write("---")  # Separator to push input to the bottom
        #     with st.container():
        #         # Create a horizontal layout for the input box and buttons
        #         col1, col2, col3 = st.columns([1, 8, 1])

        #         with col1:
        #             if st.button("Refresh Chat", key="refresh_button"):
        #                 st.session_state.refresh_trigger += 1  # Trigger a manual refresh

        #         with col2:
        #             # Input box for typing messages
        #             message = st.text_input(
        #                 "Message Input",  # Non-empty label
        #                 value=st.session_state.current_input,
        #                 placeholder="Type your message here...",
        #                 key="message_input_unique",
        #                 label_visibility="collapsed"  # Hide the label visually
        #             )

        #         with col3:
        #             if st.button("Send", key="send_button"):
        #                 st.session_state.refresh_trigger += 1 
        #                 if message.strip():
        #                     st.session_state.client.send_message(f"{name}: {message.strip()}")
        #                     st.session_state.messages.append((datetime.now().strftime("%H:%M:%S"), name, message.strip()))
        #                     st.session_state.current_input = ""  # Reset the
        #                 st.session_state.refresh_trigger += 1 

# Only display the chat interface if the user is logged in
        if st.session_state.logged_in:
            st.write(f"Welcome to the chatroom, {st.session_state.current_user}!")

            # Message container
            message_container = st.empty()
            with message_container:
                # Start the container div
                messages_html = (
                    f"<div style='height:400px; overflow-y:auto; padding:10px; border:1px solid #ddd; background-color:#e0ffff; border-radius: 5px;'>"
                )
                for msg in st.session_state.messages:
                    if len(msg) == 3:  # Ensure message has the expected format
                        timestamp, username, message = msg
                        user_color = hash(username) % 360  # Generate a unique color for each username
                        
                        # Add each message to the container
                        messages_html += (
                            f"<p style='margin:5px 0;'>"
                            f"<span style='color:gray;'>[{timestamp}]</span> "
                            f"<span style='color:hsl({user_color}, 70%, 50%); font-weight:bold;'>{username}:</span> "
                            f"{message}"
                            f"</p>"
                        )
                # Close the container div
                messages_html += "</div>"

                # Render the entire HTML content
                st.markdown(messages_html, unsafe_allow_html=True)

            # Input box and buttons at the bottom of the page
            if "current_input" not in st.session_state:
                st.session_state.current_input = ""

            st.write("---")  # Separator to push input to the bottom
            with st.container():
                # Create a horizontal layout for the input box and buttons
                col1, col2, col3 = st.columns([1, 8, 1])

                with col1:
                    # Button to refresh the chat
                    if st.button("Refresh Chat", key="refresh_button"):
                        st.session_state.refresh_trigger += 1  # Increment the refresh trigger

                with col2:
                    # Input box for typing messages
                    message = st.text_input(
                        "Message Input",  # Non-empty label
                        value=st.session_state.current_input,
                        placeholder="Type your message here...",
                        key="message_input_unique",
                        label_visibility="collapsed"  # Hide the label visually
                    )

                with col3:
                    # Button to send a message
                    if st.button("Send", key="send_button"):
                        # Trigger a pre-send refresh
                        st.session_state.refresh_trigger += 1

                        # Send the message
                        if message.strip():
                            st.session_state.client.send_message(f"{st.session_state.current_user}: {message.strip()}")
                            st.session_state.messages.append(
                                (datetime.now().strftime("%H:%M:%S"), st.session_state.current_user, message.strip())
                            )
                            st.session_state.current_input = ""  # Reset the input field

                        # Trigger another refresh after sending
                        st.session_state.refresh_trigger += 1




if __name__ == "__main__":
    main()

