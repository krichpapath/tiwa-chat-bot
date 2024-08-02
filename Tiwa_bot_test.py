# Define functions to be run when a word is matched
def play_sound():
    print("Playing sound...")

def display_message():
    print("Displaying message...")

def send_notification():
    print("Sending notification...")

# Dictionary mapping words to functions
word_to_function = {
    "PLAY_SOUND": play_sound,
    "DISPLAY_MESSAGE": display_message,
    "SEND_NOTIFICATION": send_notification
}

# Function to check for a word in the list and run the corresponding function
def check_and_execute(commands):
    for command in commands:
        if command in word_to_function:
            print(f"Command '{command}' detected. Executing associated function...")
            word_to_function[command]()
        else:
            print(f"No function associated with command '{command}'.")

# Example list of commands
commands_list = ["PLAY_SOUND", "DISPLAY_MESSAGE", "INVALID_COMMAND", "SEND_NOTIFICATION"]

# Check for commands and execute corresponding functions
check_and_execute(commands_list)
