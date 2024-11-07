import customtkinter as ctk
from PIL import Image, ImageFont
from Tiwa_chatgpt import TiwaChatGPT
from Tiwa_voice import Tiwa_SpeechRecognizer
import pytz
from datetime import datetime
import textwrap
import cv2, time
from threading import Thread

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Tiwa Chatbot")
app.geometry("1920x1080")

# Font settings
custom_font_path = "Layiji MaHaNiYom V1.61"
custom_font = custom_font_path

# Initialize Tiwa components
tiwaSpeechRecognizer = Tiwa_SpeechRecognizer()
tiwaChatGPT = TiwaChatGPT()

# Header Frame
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(fill="x", padx=20, pady=(20, 0))

# Header Label
header_label = ctk.CTkLabel(
    header_frame,
    text="Hey, Tiwa's Here !!! Talk to me, I’m all ears! ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧",
    font=(custom_font, 45),
    width=50,
    height=50,
)
header_label.pack(side="left", padx=20, pady=20)

# Reset Button (Forget Memory Button)
reset_button = ctk.CTkButton(
    header_frame,
    text="⟳ Reset",
    width=120,
    height=60,
    font=(custom_font, 26),
    fg_color="#E63946",
    command=lambda: reset_chat(),  # Reset function call
)
reset_button.pack(side="left", padx=20, pady=20)

# Main Chat Frame
chat_frame = ctk.CTkFrame(
    app,
    fg_color="transparent",
    width=1250,
    height=500,
)
chat_frame.pack(fill="x", padx=20, pady=(0, 20))

# Chat Box (User Question Input)
chat_box = ctk.CTkTextbox(
    chat_frame,
    width=1250,
    height=350,
    fg_color="#E63946",
    corner_radius=10,
    font=(custom_font, 40),
)
chat_box.pack(fill="y", side="left", padx=20, pady=20)

# Input Frame
input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
input_frame.pack(side="right", fill="y", padx=(0, 20), pady=20)

# Camera Box (Now using CTkImage for the webcam)
camera_box = ctk.CTkImage(
    Image.new("RGB", (320, 240), (255, 255, 255)), size=(320, 240)
)
camera_box_label = ctk.CTkLabel(
    input_frame,
    image=camera_box,
    width=320,
    height=240,
    text="",
    fg_color="transparent",
)
camera_box_label.grid(row=0, column=0, columnspan=2, pady=20)

# Left Button (Below Camera Box)
left_button = ctk.CTkCheckBox(
    input_frame,
    width=90,
    height=50,
    fg_color="#E63946",
    font=(custom_font, 30),
    text="Picture",
)
left_button.grid(row=1, column=0, padx=(20, 10), pady=40)

# Right Button (Below Camera Box)
right_button = ctk.CTkButton(
    input_frame,
    width=150,
    height=50,
    fg_color="#E63946",
    corner_radius=10,
    font=(custom_font, 40),
    text="Send >",
    command=lambda: submit_question(),  # Submit function call
)
right_button.grid(row=1, column=1, padx=(10, 20), pady=40)

# Bottom Frame (for Profile and Response Box)
bottom_frame = ctk.CTkFrame(app, fg_color="#E63946")
bottom_frame.pack(fill="both", expand=True)

# Profile Image
profile_image_path = "Tiwa_UI\\Tiwa_picture.jpg"
profile_image = Image.open(profile_image_path)
profile_image_ctk = ctk.CTkImage(profile_image, size=(200, 200))

# Profile Image Label
profile_image_label = ctk.CTkLabel(
    bottom_frame, text="", image=profile_image_ctk, width=200, height=200
)
profile_image_label.pack(fill="both", side="left", padx=60, pady=40)

# Response Frame (Scrollable Frame for responses)
response_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
response_frame.pack(fill="both", expand=True, side="left", padx=20, pady=20)

# Scrollable Frame for Response Box
scrollable_frame = ctk.CTkScrollableFrame(
    response_frame, width=1500, height=400, fg_color="transparent"
)
scrollable_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

# Response Label for displaying the answer
response_label = ctk.CTkLabel(
    scrollable_frame,
    text="Your response text will appear here...",
    width=1480,
    height=380,
    fg_color="white",
    corner_radius=10,
    font=(custom_font, 40),
    anchor="nw",
    justify="left",
    text_color="black",
)
response_label.pack(padx=10, pady=10)


def submit_question():
    question = chat_box.get("1.0", "end-1c").strip()
    if not question:
        response_label.configure(text="คุยกับหนูได้เลยนะคะ ⸜(｡˃ ᵕ ˂ )⸝♡")
        return

    thailand_tz = pytz.timezone("Asia/Bangkok")
    current_time = datetime.now(thailand_tz).isoformat()

    if left_button.get():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame_rgb)
            image_path = "temp_image.jpg"
            frame_image.save(image_path)
            try:
                response = tiwaChatGPT.chat_with_gpt_picture_base64(
                    f"{question}, Current Time is {current_time}", image_path
                )
                wrapped_response = wrap_text(response, 90)
                response_label.configure(text=f"Response: {wrapped_response}")
            except Exception as e:
                response_label.configure(
                    text="An error occurred while processing the question."
                )
                print(f"Error: {e}")
        else:
            response_label.configure(text="Unable to capture the webcam image.")
    else:
        try:
            # Send only the question and current time if the checkbox is not checked
            response = tiwaChatGPT.chat_with_gpt(
                f"{question}, Current Time is {current_time}"
            )
            wrapped_response = wrap_text(response, 90)
            response_label.configure(text=f"Response: {wrapped_response}")
        except Exception as e:
            response_label.configure(
                text="An error occurred while processing the question."
            )
            print(f"Error: {e}")


def reset_chat():
    chat_box.delete("1.0", "end")
    tiwaChatGPT.forget()
    response_label.configure(text="Memory cleared! Tiwa โดนลบความทรงจำแล้ว!")


def wrap_text(text, max_width):
    words = text.split()
    wrapped_text = ""
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_width:
            current_line += " " + word if current_line else word
        else:
            wrapped_text += current_line + "\n"
            current_line = word
    wrapped_text += current_line
    return wrapped_text


def start_webcam():
    global cap, running
    cap = cv2.VideoCapture(0)
    running = True

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame_rgb)
            frame_image = frame_image.resize((320, 240))
            frame_image_ctk = ctk.CTkImage(frame_image, size=(320, 240))
            camera_box_label.configure(image=frame_image_ctk)

        app.after(50, update_frame)

    update_frame()


start_webcam()

app.mainloop()
