import os
import ast
import pandas as pd
from scipy import spatial
from openai import OpenAI
from dotenv import load_dotenv
from rich import print
import tiktoken

load_dotenv()


class Tiwa_GPTEmbedding:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
        self.embedding_model = "text-embedding-3-small"

    def get_embedding(self, text):
        response = self.client.embeddings.create(input=text, model=self.embedding_model)
        # print(f"[coral]EMBEDEDEDEDDEDEDEDEDEDDEDEDEDEDEDDEDEDEDEDEDDEDEDEDEDEDDEDEDEDEDEDDEDE {text}")
        return response.data[0].embedding

    def num_tokens_from_string_embedding(self, string: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(string))

    def create_embedding_file_using_chat_log(
        self, embedding_data_path: str, chat_log_path: str
    ):
        with open(chat_log_path, "r", encoding="utf-8") as file:
            data = file.read()
        parsed_data = ast.literal_eval(data)
        df = pd.DataFrame(parsed_data).iloc[1:]
        df["text"] = (
            "Role: " + df.role.str.strip() + "; Content: " + df.content.str.strip()
        )
        df["embedding"] = df.text.apply(lambda x: self.get_embedding(x))
        df.to_csv(embedding_data_path, index=False)

    def add_embedding_text(
        self, text: dict, embedding_data_path: str, precomputed_embedding=None
    ):
        role = text["role"]
        content = text["content"].strip()
        combined_text = f"Role: {role}; Content: {content}"
        embedding = (
            precomputed_embedding
            if precomputed_embedding is not None
            else self.get_embedding(combined_text)
        )

        new_data = {
            "role": role,
            "content": content,
            "text": combined_text,
            "embedding": embedding,
        }
        new_df = pd.DataFrame([new_data])

        if os.path.exists(embedding_data_path):
            existing_df = pd.read_csv(embedding_data_path)
            if existing_df.empty:
                print(
                    "Text already empty as the most recent entry in the embedding file."
                )
            else:
                updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                updated_df.to_csv(embedding_data_path, index=False)
        else:
            new_df.to_csv(embedding_data_path, index=False)

    def load_embedding(self, embedding_data_path: str) -> pd.DataFrame:
        if (
            not os.path.exists(embedding_data_path)
            or os.stat(embedding_data_path).st_size == 0
        ):
            return pd.DataFrame(columns=["role", "content", "text", "embedding"])
        df = pd.read_csv(embedding_data_path)
        df["embedding"] = df["embedding"].apply(ast.literal_eval)
        return df

    def strings_ranked_by_relatedness(
        self,
        prompt: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 3,
    ) -> tuple[list[str], list[float], list[float]]:
        new_prompt = f"Role: user; Content: {prompt}"
        query_embedding = self.get_embedding(new_prompt)
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        if strings_and_relatednesses:
            strings, relatednesses = zip(*strings_and_relatednesses)
            return strings[:top_n], relatednesses[:top_n], query_embedding
        else:
            return [], [], ""

    def strings_ranked_by_relatedness_add_recent(
        self,
        prompt: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 3,
    ) -> tuple[list[tuple[str, str]], list[float], list[float]]:
        query_embedding = self.get_embedding(prompt)

        if len(df) > 2:
            df_excluded = df.iloc[:-2]
            df_last_two = df.iloc[-2:]
        else:
            df_excluded = df
            df_last_two = pd.DataFrame()

        strings_and_relatednesses = [
            (
                (row["content"], row["role"]),
                relatedness_fn(query_embedding, row["embedding"]),
            )
            for i, row in df_excluded.iterrows()
        ]
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)

        if strings_and_relatednesses:
            strings_with_roles, relatednesses = zip(*strings_and_relatednesses)
            top_strings_with_roles = list(strings_with_roles[:top_n])
            top_relatednesses = list(relatednesses[:top_n])
        else:
            top_strings_with_roles = []
            top_relatednesses = []

        if not df_last_two.empty:
            for i, row in df_last_two.iterrows():
                top_strings_with_roles.append((row["content"], row["role"]))
                top_relatednesses.append(
                    relatedness_fn(query_embedding, row["embedding"])
                )

        return top_strings_with_roles, top_relatednesses, query_embedding

    def create_prompt_message(
        self,
        first_message: str,
        prompt: str,
        embedding_data_path: str,
        token_budget: int,
    ) -> tuple[list[dict], list[float]]:
        # Load embedding data
        df = self.load_embedding(embedding_data_path)
        print(f"DICK DICK\n{df}")  # Debug print statement

        message_array = []

        if not df.empty:
            # Get related chat history and relatedness scores
            chat_history, relatednesses, embedding_prompt = (
                self.strings_ranked_by_relatedness_add_recent(prompt, df, top_n=3)
            )

            # Append related chat history to the message array
            for chat, role in chat_history:
                message_array.append({"role": role, "content": chat})

            # Add user response to the message array
            message_array.append({"role": "user", "content": prompt})

            # Calculate token count
            num_tokens = self.num_tokens_from_string_embedding(
                " ".join([msg["content"] for msg in message_array])
            )
            print(
                f"[blue] Total embedding prompt token is {num_tokens}"
            )  # Debug print statement

            if num_tokens > token_budget:
                raise ValueError(
                    f"Too much token, overflow token budget. Tokens used: {num_tokens}"
                )
            return message_array, embedding_prompt

        else:
            # Handle empty DataFrame case
            embedding_prompt = self.get_embedding(f"Role: user; Content: {prompt}")
            num_tokens = self.num_tokens_from_string_embedding(
                f"Role: user; Content: {prompt}"
            )
            print(
                f"[blue] Total embedding prompt token is {num_tokens}"
            )  # Debug print statement

            if num_tokens > token_budget:
                raise ValueError(
                    f"Too much token, overflow token budget. Tokens used: {num_tokens}"
                )
            return [{"role": "user", "content": prompt}], embedding_prompt
