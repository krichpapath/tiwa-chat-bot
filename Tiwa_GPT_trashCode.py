import os
import ast
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
from rich import print
from Tiwa_embedding import Tiwa_GPTEmbedding
from Tiwa_drawing import Tiwa_drawing
import keyboard
import json

load_dotenv()


class TiwaChatGPT:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
        self.chat_log = []
        self.chat_log_path = "Tiwa_memory/TiwaChatLog.txt"
        self.chat_backup_path = "Tiwa_memory/TiwaChatLogBackUp.txt"
        self.embedding_chat_log_path = "Tiwa_memory/embedded_memory.csv"
        self.model = "gpt-4o"  # gpt-3.5-turbo-0125
        self.token_max = 3000
        self.tiwaEmbedding = Tiwa_GPTEmbedding()
        # self.tiwaDrawing = Tiwa_drawing()
        self.load_chat_history()
        self.initialize_chat_log()
        self.memory_limit = 20

    def load_chat_history(self):
        if (
            os.path.exists(self.chat_log_path)
            and os.stat(self.chat_log_path).st_size > 0
        ):
            with open(self.chat_log_path, "r", encoding="utf-8") as file:
                self.chat_log = ast.literal_eval(file.read())

    def load_first_message(self) -> str:
        try:
            with open(
                "Tiwa_prompt\Tiwa daughter prompt.txt", "r", encoding="utf-8"
            ) as file:
                data = file.read()
            return data
        except FileNotFoundError:
            raise FileNotFoundError("The file was not found.")
        except IOError:
            raise IOError("An error occurred while reading the file.")

    def initialize_chat_log(self):
        if len(self.chat_log) == 0:
            first_system_message = {
                "role": "system",
                "content": self.load_first_message(),
            }
            print(f"[yellow]{len(self.chat_log)}")
            self.chat_history_append_no_embedding(first_system_message)

    def chat_history_append_no_embedding(self, messages):
        while len(self.chat_log) >= self.memory_limit:
            self.chat_log = [self.chat_log[0]] + self.chat_log[2:]
        self.chat_log.append(messages)
        with open(self.chat_log_path, "w", encoding="utf-8") as file:
            file.write(str(self.chat_log))
        with open(self.chat_backup_path, "a", encoding="utf-8") as file:
            file.write(str(self.chat_log)[1:-1] + "\n")

    def chat_history_append(self, messages, embedding=None):
        while len(self.chat_log) >= self.memory_limit:
            self.chat_log = [self.chat_log[0]] + self.chat_log[2:]
        self.chat_log.append(messages)
        with open(self.chat_log_path, "w", encoding="utf-8") as file:
            file.write(str(self.chat_log))
        if embedding is None:
            self.tiwaEmbedding.add_embedding_text(
                messages, self.embedding_chat_log_path
            )
        else:
            self.tiwaEmbedding.add_embedding_text(
                messages, self.embedding_chat_log_path, precomputed_embedding=embedding
            )
        with open(self.chat_backup_path, "a", encoding="utf-8") as file:
            file.write(str(self.chat_log)[1:-1] + "\n")

    def chat_with_gpt(self, prompt):
        if not prompt:
            print("Didn't receive input!")
            return
        messages = {"role": "user", "content": prompt}
        self.chat_history_append(messages)
        print(
            f"[yellow]Asking ChatGPT a question...Token usage is {self.num_tokens_from_messages(self.chat_log)}"
        )
        if self.num_tokens_from_messages(self.chat_log) > self.token_max:
            print("The length of this chat question is too large for the GPT model")
            self.forget()

        response = self.openai.chat.completions.create(
            model=self.model, messages=self.chat_log
        )
        response_message = {
            "role": response.choices[0].message.role,
            "content": response.choices[0].message.content,
        }
        self.chat_history_append(response_message)
        return response.choices[0].message.content

    def chat_with_gpt_no_history(self, prompt):
        if not prompt:
            print("Didn't receive input!")
            return
        messages = [{"role": "user", "content": prompt}]
        print(
            f"[yellow]Asking ChatGPT a question...Token usage is {self.num_tokens_from_messages(self.chat_log)}"
        )
        if self.num_tokens_from_messages(messages) > self.token_max:
            print("The length of this chat question is too large for the GPT model")
            return

        response = self.openai.chat.completions.create(
            model=self.model, messages=messages
        )
        return response.choices[0].message.content

    def chat_with_gpt_one_history(self, system_prompt, prompt):
        if not prompt:
            print("Didn't receive input!")
            return
        first_message = {"role": "system", "content": system_prompt}
        user_message = {"role": "user", "content": prompt}
        messages_list = [first_message, user_message]

        print(
            f"[yellow]Asking ChatGPT a question...Token usage is {self.num_tokens_from_messages(messages_list)}"
        )
        if self.num_tokens_from_messages(messages_list) > self.token_max:
            print("The length of this chat question is too large for the GPT model")
            return

        response = self.openai.chat.completions.create(
            model=self.model, messages=messages_list
        )
        return response.choices[0].message.content

    def chat_with_gpt_picture(self, prompt, url):
        if not prompt or not url or (self.model != "gpt-4o"):
            print("Didn't receive input! or wrong version of gpt")
            return

        messages = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": url}},
            ],
        }
        first_system_message = {"role": "system", "content": self.load_first_message()}
        messages_list = [first_system_message, messages]

        self.chat_history_append(
            {
                "role": "user",
                "content": f"User give you this picture and say '{prompt}'",
            }
        )
        # print(f"[yellow]Asking ChatGPT a question...Token usage is {self.num_tokens_from_messages(messages_list)}")
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=messages_list,
        )
        self.chat_history_append(
            {
                "role": "assistant",
                "content": f"User give you a picture and you respond with {response.choices[0].message.content}",
            }
        )
        print(str(response.choices[0].message.content))
        return response.choices[0].message.content

    def chat_with_gpt_embedding_chat_log(self, prompt: str) -> str:
        if prompt == "":
            print("Didn't receive input!")
            return
        first_message = "Use the following chat log to continue and guide the conversation effectively."
        messages, embedding_message = self.tiwaEmbedding.create_prompt_message(
            first_message,
            prompt,
            embedding_data_path=self.embedding_chat_log_path,
            token_budget=self.token_max,
        )
        system_message = self.load_first_message()
        messages_list = [{"role": "system", "content": system_message}]

        # Append messages from the generated message array
        messages_list.extend(messages)

        # Print input messages for debugging
        print("Message Input:", messages_list)

        # Append the user's prompt to the message array
        prompt_message = {"role": "user", "content": prompt}
        self.chat_history_append(prompt_message, embedding_message)

        # Calculate token usage
        token_usage = self.num_tokens_from_messages(messages_list)
        print(f"[yellow]Asking ChatGPT a question...Token usage is {token_usage}")

        # Get response from ChatGPT
        response = self.openai.chat.completions.create(
            model=self.model, messages=messages_list
        )
        response_message = {
            "role": response.choices[0].message.role,
            "content": response.choices[0].message.content,
        }

        # Append response to chat history
        self.chat_history_append(response_message)

        return response.choices[0].message.content

    def num_tokens_from_messages(self, messages) -> int:
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for message in messages:
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens -= 1  # role is always required and always 1 token

        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def chat(self):
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "die"]:
                print("[yellow]Sayonara! 🥹")
                break
            if user_input.lower() in ["forget"]:
                self.forget()
                break
            # response = self.chat_with_gpt_picture(user_input,"https://media.discordapp.net/attachments/966386008390258711/1257341175334047744/will-smith-attends-varietys-creative-impact-awards-and-10-directors-to-watch-brunch-at-the-parker-palm-springs-on-january-3-2016-in-palm-springs-california-photo-by-jerod-harrisgetty-images.jpg?ex=66840db8&is=6682bc38&hm=8104e794b9d22ac4ecf420b5f8133160fb881fe90218d3f7823c8f89725d4d42&=&format=webp&width=703&height=703")
            # response = self.chat_with_gpt_embedding_chat_log(user_input)
            response = self.chat_with_gpt_embedding_and_drawing(user_input)
            if response:
                print(f"[green]Chatbot:\n{response}\n")

    def forget(self):
        try:
            open(self.chat_log_path, "w").close()
            self.chat_log = []
            if os.path.exists(self.embedding_chat_log_path):
                os.remove(self.embedding_chat_log_path)
            print(f"Successfully cleared data from {self.chat_log_path}")
            first_system_message = {
                "role": "system",
                "content": self.load_first_message(),
            }
            self.chat_history_append_no_embedding(first_system_message)
        except FileNotFoundError:
            print(
                f"File '{self.chat_log_path}' or '{self.embedding_chat_log_path}' not found."
            )
        except IOError as e:
            print(f"Error accessing or writing to file: {e}")


if __name__ == "__main__":
    bot = TiwaChatGPT()
    bot.chat()
