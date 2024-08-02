import os
from dotenv import load_dotenv
from rich import print
import tiktoken
from auto1111sdk import (
    civit_download,
    download_realesrgan,
    RealEsrganPipeline,
    StableDiffusionPipeline,
    EsrganPipeline,
)
from PIL import Image
import torch


class Tiwa_drawing:
    def __init__(self):
        load_dotenv()

        # Print torch version and CUDA status
        print("Torch version:", torch.__version__)
        print("Is CUDA enabled?", torch.cuda.is_available())

        # Model path and URL
        self.model_path = "Tiwa_drawing_model\Everyone has a heart that yearns for a better life_v1.safetensors"
        self.vae_path = "Tiwa_drawing_model\kl-f8-anime2.ckpt"
        self.upscaler_path = "Tiwa_drawing_model\\RealESRGAN_x4plus_anime_6B.pth"

        # Stable Diffusion pipeline initialization
        print(f"Text to image, model={self.model_path}")
        print("AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
        self.pipe = StableDiffusionPipeline(self.model_path)
        # self.pipe.set_vae(self.vae_path)
        self.upscaler = EsrganPipeline(self.upscaler_path)

        # Text to image parameters
        self.prompt = "(extremely,detailed,masterpiece,8k), best quality, 1girl, full body ,large red eyes, (long hair ,brown hair ,high ponytail), red and white sailor uniform , (red jacket:1.5) , large red bow , (highly detailed background),"
        self.negative_prompt = "NSFW, (worst quality: 2) , (low quality: 2), (normal quality: 2), lowres, normal quality, (monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spots, (ugly: 1.331), (duplicate: 1.331), (morbid: 1.21), ( mutilated: 1.21), (tranny: 1.331), mutated hands, (pronounced drawn hands: 1.5), blurry, (bad anatomy: 1.21), (bad anatomy: 1.21), (bad breathing: 1.331), (missing arms: 1.331), (extra extra legs: 1.331), (fused fingers: 1.61051), (too many fingers: 1.61051), (pointed eyes: 1.331), lower, bad hands, missing fingers, extra digit, bad hands, missing fingers, ((extra arms and legs))), nsfw"
        self.num_images = 1
        self.height = 540
        self.width = 960
        self.steps = 30
        self.output_path = "Tiwa_drawing/txt2img.png"
        self.cfg_scale = 10
        self.seed = -1
        self.sampler_name = "DPM++ 2M Karras"
        # ["Euler a", "Euler", "LMS", "Heun", "DPM2", "DPM2 a",
        #  "DPM++ 2S a", "DPM++ 2M", "DPM fast", "DPM adaptive",
        #  "LMS Karras", "DPM2 Karras", "DPM2 a Karras",
        #  "DPM++ 2S a Karras", "DPM++ 2M Karras", "DDIM", "PLMS"]

    def generate_image(self, user_prompt: str = None):
        new_prompt = f"{self.prompt}{user_prompt}"
        output = self.pipe.generate_txt2img(
            num_images=self.num_images,
            cfg_scale=self.cfg_scale,
            sampler_name=self.sampler_name,
            seed=self.seed,
            prompt=new_prompt,
            height=self.height,
            width=self.width,
            negative_prompt=self.negative_prompt,
            steps=self.steps,
        )

        unique_output_path = self.uniquify(self.output_path)
        output[0].save(unique_output_path)

        image = Image.open(unique_output_path)
        upscale_output = self.upscaler.upscale(img=image, scale=2)

        # upscale_output = self.pipe.sd_upscale_img2img(prompt = self.prompt, init_image= image, upscaler = self.upscaler , scale_factor = 2,
        #     negative_prompt = self.negative_prompt, steps = 10 ,denoising_strength = 0.4)
        upscale_output.save(unique_output_path)
        if os.path.exists(unique_output_path):
            print(f"Text to Image output generated: {unique_output_path}")
            return unique_output_path
        else:
            print(f"Error: output file not found {unique_output_path}")

    @staticmethod
    def uniquify(path):
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = f"{filename} ({counter}){extension}"
            counter += 1

        return path

    # def chat_with_gpt_drawing(self, prompt: str):
    #         # Step 1: send the conversation and available functions to the model
    #         messages = [
    #             {
    #                 "role": "system",
    #                 "content": "If you feel it's necessary or it's a command , you can choose to draw a picture .Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
    #             },
    #             {
    #                 "role": "user",
    #                 "content": prompt,
    #             },
    #         ]

    #         tools = [
    #             {
    #                 "type": "function",
    #                 "function": {
    #                     "name": "get_drawing",
    #                     "description": "Create a picture/drawing of the current scene",
    #                     "parameters": {
    #                         "type": "object",
    #                         "properties": {
    #                             "keywords": {
    #                                 "type": "string",
    #                                 "description": "Keywords describing the current scene. Must contain 4 to 10 words at least, separated by commas.",
    #                             }
    #                         },
    #                         "required": ["keywords"],
    #                     },
    #                 },
    #             }
    #         ]
    #         response = self.openai.chat.completions.create(
    #             model=self.model,
    #             messages=messages,
    #             tools=tools,
    #             tool_choice="auto",
    #         )
    #         response_message = response.choices[0].message
    #         messages.append(response_message)
    #         print(f"[magenta2]{response_message}")
    #         tool_calls = response_message.tool_calls
    #         # Step 2: check if the model wanted to call a function
    #         if tool_calls:
    #             print("[orange_red1]Drawing Picture")
    #             tool_call_id = tool_calls[0].id
    #             tool_function_name = tool_calls[0].function.name
    #             tool_query_string = eval(tool_calls[0].function.arguments)["keywords"]
    #             print(f"[orange_red1]{tool_query_string}")
    #             # Step 3: Call the function and retrieve results. Append the results to the messages list.
    #             if tool_function_name == "get_drawing":
    #                 results = self.tiwaDrawing.generate_image(user_prompt=tool_query_string)

    #                 messages.append(
    #                     {
    #                         "role": "tool",
    #                         "tool_call_id": tool_call_id,
    #                         "name": tool_function_name,
    #                         "content": results,
    #                     }
    #                 )
    #                 print(f"[cyan]{messages}")
    #                 model_response_with_function_call = self.openai.chat.completions.create(
    #                     model=self.model,
    #                     messages=messages,
    #                 )
    #                 print(model_response_with_function_call.choices[0].message.content)
    #             else:
    #                 print(f"Error: function {tool_function_name} does not exist")
    #         else:
    #             print(response_message.content)

    #     def chat_with_gpt_embedding_and_drawing(self, prompt: str) -> str:
    #         if prompt == "":
    #             print("Didn't receive input!")
    #             return
    #         first_message = "Use the following chat log to continue and guide the conversation effectively."
    #         messages, embedding_message = self.tiwaEmbedding.create_prompt_message(
    #             first_message,
    #             prompt,
    #             embedding_data_path=self.embedding_chat_log_path,
    #             token_budget=self.token_max,
    #         )
    #         system_message = self.load_first_message()
    #         messages_list = [{"role": "system", "content": system_message}]
    #         drawing_messages_list = []
    #         # Append messages from the generated message array
    #         messages_list.extend(messages)

    #         # Append the user's prompt to the message array
    #         prompt_message = {"role": "user", "content": prompt}
    #         self.chat_history_append(prompt_message, embedding_message)

    #         # Calculate token usage
    #         token_usage = self.num_tokens_from_messages(messages_list)
    #         print(f"[yellow]Asking ChatGPT a question...Token usage is {token_usage}")

    #         messages_list.append(
    #             {
    #                 "role": "system",
    #                 "content": "If you feel it's appropriate or if it's a command, you can choose to draw a picture. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
    #             }
    #         )
    #         tools = [
    #             {
    #                 "type": "function",
    #                 "function": {
    #                     "name": "get_drawing",
    #                     "description": "Create a picture/drawing/วาดรูป/รูปภาพ of the current scene",
    #                     "parameters": {
    #                         "type": "object",
    #                         "properties": {
    #                             "keywords": {
    #                                 "type": "string",
    #                                 "description": "Keywords describing the current scene. Must contain at least 4 to 10 english words, separated by commas.",
    #                             }
    #                         },
    #                         "required": ["keywords"],
    #                     },
    #                 },
    #             }
    #         ]
    #         drawing_response = self.openai.chat.completions.create(
    #             model=self.model,
    #             messages=messages_list,
    #             tools=tools,
    #             tool_choice="auto",
    #         )
    #         if drawing_response.choices[0].content != None:
    #             self.chat_history_append(
    #                 {
    #                     "role": drawing_response.choices[0].message.role,
    #                     "content": drawing_response.choices[0].message.content,
    #                 }
    #             )
    #         messages_list.append(drawing_response.choices[0])
    #         tool_calls = drawing_response.choices[0].message.tool_calls

    #         # Check if the model wanted to call a function
    #         if tool_calls:
    #             tool_call_id = tool_calls[0].id
    #             tool_function_name = tool_calls[0].function.name
    #             tool_query_string = eval(tool_calls[0].function.arguments)["keywords"]
    #             print("[orange_red1]Drawing Picture")
    #             print(f"[orange_red1]{tool_query_string}")

    #             # Call the function and retrieve results. Append the results to the messages list.
    #             if tool_function_name == "get_drawing":
    #                 results = self.tiwaDrawing.generate_image(user_prompt=tool_query_string)
    #                 messages_list.append(
    #                     {
    #                         "role": "tool",
    #                         "tool_call_id": tool_call_id,
    #                         "name": tool_function_name,
    #                         "content": results,
    #                     }
    #                 )
    #                 model_response_with_function_call = self.openai.chat.completions.create(
    #                     model=self.model,
    #                     messages=messages_list,
    #                 )
    #                 print(
    #                     "model_response_with_function_call.choices[0].message.content"
    #                     + model_response_with_function_call.choices[0].message.content
    #                 )
    #                 self.chat_history_append(
    #                     {
    #                         "role": model_response_with_function_call.choices[
    #                             0
    #                         ].message.role,
    #                         "content": model_response_with_function_call.choices[
    #                             0
    #                         ].message.content,
    #                     }
    #                 )
    #                 return drawing_response.choices[0].message.content, results
    #             else:
    #                 print(f"Error: function {tool_function_name} does not exist")
    #         else:
    #             print(
    #                 "drawing_response_message.content"
    #                 + drawing_response.choices[0].message.content
    #             )
    #         print(f"[cyan]messages_list= {messages_list}")
    #         return drawing_response.choices[0].message.content


if __name__ == "__main__":
    print("PENISSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS🥹🥹🥹🥹🥹🥹🥹")
    generator = Tiwa_drawing()
    generator.generate_image()
