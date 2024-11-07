import customtkinter as ctk
from PIL import Image, ImageFont

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Tiwa Chatbot")
app.geometry("1920x1080")

custom_font_path = "Layiji MaHaNiYom V1.61"
custom_font = custom_font_path

header_frame = ctk.CTkFrame(
    app,
    fg_color="transparent",
)
header_frame.pack(fill="x", padx=20, pady=(20, 0))

header_label = ctk.CTkLabel(
    header_frame,
    text="Hey, Tiwa's Here !!! Talk to me, I’m all ears!",
    font=(custom_font, 45),
    width=50,
    height=50,
)
header_label.pack(side="left", padx=20, pady=20)

reset_button = ctk.CTkButton(
    header_frame,
    text="⟳ Reset",
    width=120,
    height=60,
    font=(custom_font, 26),
    fg_color="#E63946",
)
reset_button.pack(side="left", padx=20, pady=20)

chat_frame = ctk.CTkFrame(
    app,
    fg_color="transparent",
    width=1250,
    height=500,
)
chat_frame.pack(fill="x", padx=20, pady=(0, 20))

chat_box = ctk.CTkTextbox(
    chat_frame,
    width=1250,
    height=350,
    fg_color="#E63946",
    corner_radius=10,
    font=(custom_font, 40),
)
chat_box.pack(fill="y", side="left", padx=20, pady=20)

input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
input_frame.pack(side="right", fill="y", padx=(0, 20), pady=20)

camera_box = ctk.CTkLabel(
    input_frame,
    width=300,
    height=220,
    fg_color="#E63946",
    corner_radius=0,
    font=(custom_font, 40),
    text="Camera",
)
camera_box.grid(row=0, column=0, columnspan=2, pady=20)

left_button = ctk.CTkCheckBox(
    input_frame,
    width=90,
    height=50,
    fg_color="#E63946",
    font=(custom_font, 30),
    text="Picture",
)
left_button.grid(row=1, column=0, padx=(20, 10), pady=40)

right_button = ctk.CTkButton(
    input_frame,
    width=150,
    height=50,
    fg_color="#E63946",
    corner_radius=10,
    font=(custom_font, 40),
    text="Send >",
)
right_button.grid(row=1, column=1, padx=(10, 20), pady=40)

bottom_frame = ctk.CTkFrame(
    app,
    fg_color="#E63946",
)
bottom_frame.pack(fill="both", expand=True)

profile_image_path = "Tiwa_UI\\Tiwa_picture.jpg"
profile_image = Image.open(profile_image_path)
profile_image_ctk = ctk.CTkImage(profile_image, size=(200, 200))

profile_image_label = ctk.CTkLabel(
    bottom_frame, text="", image=profile_image_ctk, width=200, height=200
)
profile_image_label.pack(fill="both", side="left", padx=60, pady=40)

response_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
response_frame.pack(fill="both", expand=True, side="left", padx=20, pady=20)

scrollable_frame = ctk.CTkScrollableFrame(
    response_frame, width=1500, height=400, fg_color="transparent"
)
scrollable_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

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

app.mainloop()
