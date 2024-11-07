# # Call the OpenAI API with the chat history
#     response = openai.chat.completions.create(model="gpt-4o", messages=chat_history)

#     # Get the assistant's response
#     assistant_response = response.choices[0].message.content

import openai
import os
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font as tkFont
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API token from the environment variable
openai.api_key = os.getenv("OPENAI_TOKEN")

# Initialize chat history
chat_history = []


def chat_with_gpt4(user_input):
    # Add the user input to the chat history
    chat_history.append({"role": "user", "content": user_input})

    # Update UI to show it's waiting for a response
    output_box.insert(tk.END, "(O.O) Waiting for GPT-4 response...\n")
    output_box.see(tk.END)

    # Call the OpenAI API with the chat history
    response = openai.chat.completions.create(model="gpt-4o", messages=chat_history)

    # Get the assistant's response
    assistant_response = response.choices[0].message.content

    # Add the assistant's response to the chat history
    chat_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response


# Function to handle the 'Send' button click
def send_message():
    user_input = input_box.get("1.0", "end-1c")  # Get input from the text box
    if user_input.strip():  # Check if the input is not empty
        output_box.insert(tk.END, f"You: {user_input}\n")  # Display user's message
        input_box.delete("1.0", tk.END)  # Clear the input box

        # Get GPT-4 response
        gpt_response = chat_with_gpt4(user_input)

        # Display GPT-4's response in the output box
        output_box.insert(tk.END, f"GPT-4: {gpt_response}\n\n")

        # Update chat counter
        update_chat_count()

        output_box.see(tk.END)  # Scroll to the bottom of the output box


# Function to update chat count
def update_chat_count():
    chat_count = len(chat_history) // 2  # Each user/assistant pair is one full exchange
    chat_count_label.config(text=f"Chat History Count: {chat_count}")


# Function to handle the 'Reset' button click (clears the conversation)
def reset_conversation():
    chat_history.clear()  # Clear chat history
    output_box.delete("1.0", tk.END)  # Clear the output box
    update_chat_count()  # Reset the counter


# Create the main window
window = tk.Tk()
window.title("Chat with GPT-4")

# Set a custom font (use the font that you downloaded on your PC)
custom_font = tkFont.Font(
    family="Layiji MaHaNiYom V1.61", size=14
)  # Assuming this font is installed on your system

# Create a text area for output with a scrollbar
output_box = scrolledtext.ScrolledText(
    window, wrap=tk.WORD, width=60, height=20, font=custom_font
)
output_box.pack(pady=10)

# Create a text box for input with the same font
input_box = tk.Text(window, height=3, width=50, font=custom_font)
input_box.pack(pady=10)

# Create a label to show chat history count
chat_count_label = tk.Label(window, text="Chat History Count: 0", font=custom_font)
chat_count_label.pack(pady=5)

# Create a frame for buttons (Send and Reset)
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

# Create a 'Send' button
send_button = tk.Button(
    button_frame, text="Send", command=send_message, font=custom_font
)
send_button.pack(side=tk.LEFT, padx=10)

# Create a 'Reset' button
reset_button = tk.Button(
    button_frame, text="Reset", command=reset_conversation, font=custom_font
)
reset_button.pack(side=tk.LEFT, padx=10)

# Start the GUI loop
window.mainloop()
