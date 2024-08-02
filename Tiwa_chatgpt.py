import os, ast, json, pytz
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
from rich import print
from Tiwa_embedding import Tiwa_GPTEmbedding
from Tiwa_calendar import Tiwa_GoogleCalendarAPI
from datetime import datetime

load_dotenv()


class TiwaChatGPT:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
        self.chat_log = []
        self.paths = {
            "chat_log": "Tiwa_memory/TiwaChatLog.txt",
            "chat_backup": "Tiwa_memory/TiwaChatLogBackUp.txt",
            "embedding_log": "Tiwa_memory/embedded_memory.csv",
        }
        self.model, self.token_max = "gpt-4o", 3000
        self.tiwaEmbedding = Tiwa_GPTEmbedding()
        self.tiwaCalendar = Tiwa_GoogleCalendarAPI()
        self.load_chat_history()
        self.initialize_chat_log()
        self.memory_limit = 20

    def load_chat_history(self):
        if (
            os.path.exists(self.paths["chat_log"])
            and os.stat(self.paths["chat_log"]).st_size > 0
        ):
            with open(self.paths["chat_log"], "r", encoding="utf-8") as file:
                self.chat_log = ast.literal_eval(file.read())

    def load_first_message(self) -> str:
        try:
            with open(
                "Tiwa_prompt/Tiwa daughter prompt.txt", "r", encoding="utf-8"
            ) as file:
                return file.read()
        except (FileNotFoundError, IOError) as e:
            raise e

    def initialize_chat_log(self):
        if not self.chat_log:
            self.chat_history_append_no_embedding(
                {"role": "system", "content": self.load_first_message()}
            )

    def chat_history_append_no_embedding(self, messages):
        if len(self.chat_log) >= self.memory_limit:
            self.chat_log = [self.chat_log[0]] + self.chat_log[2:]
        self.chat_log.append(messages)
        with open(self.paths["chat_log"], "w", encoding="utf-8") as file:
            file.write(str(self.chat_log))
        with open(self.paths["chat_backup"], "a", encoding="utf-8") as file:
            file.write(str(self.chat_log)[1:-1] + "\n")

    def chat_history_append(self, messages, embedding=None):
        if len(self.chat_log) >= self.memory_limit:
            self.chat_log = [self.chat_log[0]] + self.chat_log[2:]
        self.chat_log.append(messages)
        with open(self.paths["chat_log"], "w", encoding="utf-8") as file:
            file.write(str(self.chat_log))
        self.tiwaEmbedding.add_embedding_text(
            messages, self.paths["embedding_log"], precomputed_embedding=embedding
        )
        with open(self.paths["chat_backup"], "a", encoding="utf-8") as file:
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
        messages_list = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
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
        if not (prompt and url and self.model == "gpt-4o"):
            print("Didn't receive input! or wrong version of gpt")
            return

        messages_list = [
            {"role": "system", "content": self.load_first_message()},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            },
        ]
        self.chat_history_append(
            {
                "role": "user",
                "content": f"User give you this picture and say '{prompt}'",
            }
        )
        response = self.openai.chat.completions.create(
            model=self.model, messages=messages_list
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
        if not prompt:
            print("Didn't receive input!")
            return
        first_message = "Use the following chat log to continue and guide the conversation effectively."
        messages, embedding_message = self.tiwaEmbedding.create_prompt_message(
            first_message,
            prompt,
            embedding_data_path=self.paths["embedding_log"],
            token_budget=self.token_max,
        )
        messages_list = [
            {"role": "system", "content": self.load_first_message()}
        ] + messages
        print("Message Input:", messages_list)
        prompt_message = {"role": "user", "content": prompt}
        self.chat_history_append(prompt_message, embedding_message)
        token_usage = self.num_tokens_from_messages(messages_list)
        print(f"[yellow]Asking ChatGPT a question...Token usage is {token_usage}")
        response = self.openai.chat.completions.create(
            model=self.model, messages=messages_list
        )
        response_message = {
            "role": response.choices[0].message.role,
            "content": response.choices[0].message.content,
        }
        self.chat_history_append(response_message)
        return response.choices[0].message.content

    def chat_with_gpt_with_tools(self, prompt):
        if not prompt:
            print("No input received!")
            return

        intro_message = "Use the following chat log to continue and guide the conversation effectively."
        pre_messages, prompt_embedding_msg = self.tiwaEmbedding.create_prompt_message(
            intro_message,
            prompt,
            embedding_data_path=self.paths["embedding_log"],
            token_budget=self.token_max,
        )

        system_msg = self.load_first_message()
        chat_history = [{"role": "system", "content": system_msg}]
        chat_history.extend(pre_messages)

        user_msg = {"role": "user", "content": prompt}
        self.chat_history_append(user_msg, prompt_embedding_msg)

        token_usage = self.num_tokens_from_messages(chat_history)
        print(f"[yellow]Asking ChatGPT a question...Token usage is {token_usage}")

        chat_history.append(
            {
                "role": "system",
                "content": "If applicable, you may call a calendar function. Do not make assumptions about the function's parameters. Always ask for clarification if the user's request is ambiguous.",
            }
        )

        calendar_tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_events",
                    "description": "List upcoming events on the user's calendar",
                    "parameters": {},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_event",
                    "description": "Create a new event in the user's calendar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Title of the event",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start date and time of the event in ISO 8601 format, e.g. 2024-07-27T15:00:00",
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Duration of the event in minutes, Default is 60 minutes",
                            },
                        },
                        "required": ["summary", "start_time", "duration"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_event",
                    "description": "Delete an event from the user's calendar if it exists",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "Unique identifier of the event to be deleted",
                            }
                        },
                        "required": ["event_id"],
                    },
                },
            },
        ]

        response = self.openai.chat.completions.create(
            model=self.model,
            messages=chat_history,
            tools=calendar_tools,
            tool_choice="auto",
        )

        if response.choices[0].message.content:
            self.chat_history_append(
                {
                    "role": response.choices[0].message.role,
                    "content": response.choices[0].message.content,
                }
            )

        print(f"[yellow]{response.choices[0].message.content}")
        chat_history.append(response.choices[0].message)
        tool_calls = response.choices[0].message.tool_calls

        if tool_calls:
            tool_call_id = tool_calls[0].id
            tool_name = tool_calls[0].function.name
            tool_args = json.loads(tool_calls[0].function.arguments)
            print("[orange_red1]Calling function")
            print(f"[orange_red1]{tool_args}")

            if tool_name == "list_events":
                results = self.tiwaCalendar.list_events()
                print(f"result from list_event: {results}")
                chat_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": results,
                    }
                )
                model_response_with_function_call = self.openai.chat.completions.create(
                    model=self.model,
                    messages=chat_history,
                )
                print(
                    "model_response_with_function_call.choices[0].message.content"
                    + model_response_with_function_call.choices[0].message.content
                )
                self.chat_history_append(
                    {
                        "role": model_response_with_function_call.choices[
                            0
                        ].message.role,
                        "content": model_response_with_function_call.choices[
                            0
                        ].message.content,
                    }
                )
                return model_response_with_function_call.choices[0].message.content
            elif tool_name == "create_event":
                results = self.tiwaCalendar.create_event(
                    summary=tool_args["summary"],
                    start_time=tool_args["start_time"],
                    duration=tool_args["duration"],
                )
                print(f"result from create_event: {results}")
                chat_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": results,
                    }
                )
                model_response_with_function_call = self.openai.chat.completions.create(
                    model=self.model,
                    messages=chat_history,
                )
                print(
                    "model_response_with_function_call.choices[0].message.content"
                    + model_response_with_function_call.choices[0].message.content
                )
                self.chat_history_append(
                    {
                        "role": model_response_with_function_call.choices[
                            0
                        ].message.role,
                        "content": model_response_with_function_call.choices[
                            0
                        ].message.content,
                    }
                )
                return model_response_with_function_call.choices[0].message.content
            elif tool_name == "delete_event":
                results = self.tiwaCalendar.delete_event(event_id=tool_args["event_id"])
                print(f"result from delete_event: {results}")
                chat_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": results,
                    }
                )
                model_response_with_function_call = self.openai.chat.completions.create(
                    model=self.model,
                    messages=chat_history,
                )
                print(
                    "model_response_with_function_call.choices[0].message.content"
                    + model_response_with_function_call.choices[0].message.content
                )
                self.chat_history_append(
                    {
                        "role": model_response_with_function_call.choices[
                            0
                        ].message.role,
                        "content": model_response_with_function_call.choices[
                            0
                        ].message.content,
                    }
                )
                return model_response_with_function_call.choices[0].message.content
            else:
                print(f"Error: function {tool_name} does not exist")
                results = None
        else:
            if response.choices[0].message.content:
                print(
                    "No tool Response message content: "
                    + response.choices[0].message.content
                )

        print(f"[cyan]chat_history= {chat_history}")
        return response.choices[0].message.content

    def num_tokens_from_messages(self, messages) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = sum(
            4
            + sum(
                len(encoding.encode(value)) - (1 if key == "name" else 0)
                for key, value in message.items()
            )
            for message in messages
        )
        return num_tokens + 2

    # def chat(self):
    #     while True:
    #         user_input = input("You: ").lower()
    #         if user_input in ["quit", "exit", "die"]:
    #             print("[yellow]Sayonara! 🥹")
    #             break
    #         if user_input == "forget":
    #             self.forget()
    #             break
    #         # response = self.chat_with_gpt_embedding_chat_log(user_input)
    #         response = self.chat_with_gpt_with_tools(user_input)
    #         if response:
    #             print(f"[green]Chatbot:\n{response}\n")
    def chat(self):
        while True:
            user_input = input("You: ").lower()

            # Get the current date and time in Thailand
            thailand_tz = pytz.timezone("Asia/Bangkok")
            current_time = datetime.now(thailand_tz).isoformat()

            print(f"Current time in Thailand: {current_time}")

            if user_input in ["quit", "exit", "die"]:
                print("[yellow]Sayonara! 🥹")
                break
            if user_input == "forget":
                self.forget()
                break
            # response = self.chat_with_gpt_embedding_chat_log(user_input)
            response = self.chat_with_gpt_with_tools(
                user_input + f"\ncurrent time is {current_time}"
            )
            if response:
                print(f"[green]Chatbot:\n{response}\n")

    def forget(self):
        try:
            open(self.paths["chat_log"], "w").close()
            self.chat_log = []
            if os.path.exists(self.paths["embedding_log"]):
                os.remove(self.paths["embedding_log"])
            print(f"Successfully cleared data from {self.paths['chat_log']}")
            self.chat_history_append_no_embedding(
                {"role": "system", "content": self.load_first_message()}
            )
        except (FileNotFoundError, IOError) as e:
            print(f"Error accessing or writing to file: {e}")


if __name__ == "__main__":
    bot = TiwaChatGPT()
    bot.chat()
