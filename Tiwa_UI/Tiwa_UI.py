import tkinter as tk
from tkinter import font
from Tiwa_chatgpt import TiwaChatGPT
from Tiwa_voice import Tiwa_SpeechRecognizer

# Initialize Tiwa components
tiwaSpeechRecognizer = Tiwa_SpeechRecognizer()
tiwaChatGPT = TiwaChatGPT()

# Color Palette (Earth Tones)
BACKGROUND_COLOR = "#F4EDE4"  # Soft beige
INPUT_BG_COLOR = "#E6D6C6"  # Light tan
BUTTON_BG_COLOR = "#A98B73"  # Muted brown
BUTTON_HOVER_COLOR = "#B6A493"  # Soft taupe
TEXT_COLOR = "#3B302A"  # Deep brown
ACCENT_COLOR = "#4F3D33"  # Darker accent brown


def submit_question():
    question = question_entry.get("1.0", tk.END).strip()
    if not question:
        response_text.set("Please enter a question.")
        return
    try:
        response = tiwaChatGPT.chat_with_gpt_embedding_chat_log(question)
        response_text.set(response)
    except Exception as e:
        response_text.set("An error occurred while processing the question.")
        print(f"Error: {e}")


def record_and_transcribe():
    try:
        audio = tiwaSpeechRecognizer.record_audio()
        output_text = tiwaSpeechRecognizer.transcribe_audio(audio)
        if output_text:
            response = tiwaChatGPT.chat_with_gpt_embedding_chat_log(output_text)
            response_text.set(f"You said: {output_text}\nResponse: {response}")
        else:
            response_text.set("No transcription available from audio.")
    except Exception as e:
        response_text.set("An error occurred during audio transcription.")
        print(f"Error: {e}")


def forget_memory():
    tiwaChatGPT.forget()
    response_text.set("Memory cleared! Tiwa โดนลบความทรงจำแล้ว🤵🏾‍♂️✨!")


# Set up the main application window
app = tk.Tk()
app.title("Tiwa Chat Interface")
app.configure(bg=BACKGROUND_COLOR)

# Load custom font after the root window is created

custom_font_path = "Tiwa_src/LayijiMahaniyomV1_61.ttf"
app_font = font.Font(family="Layiji Mahaniyom V1", size=12)
title_font = font.Font(family="Layiji Mahaniyom V1", size=16, weight="bold")

# Title Label
title_label = tk.Label(
    app, text="Tiwa Chat Interface", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=title_font
)
title_label.pack(pady=10)

# Input Text Area for entering questions
question_entry = tk.Text(
    app, height=5, width=50, bg=INPUT_BG_COLOR, fg=TEXT_COLOR, font=app_font
)
question_entry.pack(pady=10, padx=20, fill="both", expand=True)


# Function to style buttons
def style_button(button):
    button.configure(
        bg=BUTTON_BG_COLOR,
        fg=TEXT_COLOR,
        font=app_font,
        activebackground=BUTTON_HOVER_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        borderwidth=0,
        padx=10,
        pady=5,
    )


# Submit Button for text questions
submit_button = tk.Button(app, text="Submit Question", command=submit_question)
style_button(submit_button)
submit_button.pack(pady=5, fill="x")

# Record Button for audio recording
record_button = tk.Button(app, text="Record Audio", command=record_and_transcribe)
style_button(record_button)
record_button.pack(pady=5, fill="x")

# Forget Memory Button to clear chat history
forget_button = tk.Button(app, text="Forget Memory", command=forget_memory)
style_button(forget_button)
forget_button.pack(pady=5, fill="x")

# Response Display Label
response_text = tk.StringVar()
response_label = tk.Label(
    app,
    textvariable=response_text,
    wraplength=400,
    justify="left",
    bg=BACKGROUND_COLOR,
    fg=ACCENT_COLOR,
    font=app_font,
    padx=10,
    pady=10,
)
response_label.pack(pady=10, padx=20, fill="both", expand=True)


# Function to adjust font size dynamically based on window size
def resize_widgets(event):
    new_width = event.width
    new_height = event.height
    # Adjust font size based on window dimensions
    new_font_size = max(12, int(new_width / 60))
    app_font.configure(size=new_font_size)
    title_font.configure(size=new_font_size + 4)


# Bind the resize event to the `resize_widgets` function
app.bind("<Configure>", resize_widgets)

# Run the application
app.geometry("1200x800")  # Start with a reasonable default size
app.mainloop()
