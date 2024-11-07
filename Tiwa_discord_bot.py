import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Tiwa_chatgpt import TiwaChatGPT
from Tiwa_voice import Tiwa_SpeechRecognizer
import keyboard

# Load environment variables from .env file
load_dotenv()

# Set up Discord intents and bot client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize Tiwa components
tiwaSpeechRecognizer = Tiwa_SpeechRecognizer()
client = commands.Bot(command_prefix=["ทิวา! ", "Tiwa! ", "tiwa! "], intents=intents)
tiwaChatGPT = TiwaChatGPT()

# Channel ID for sending audio messages
CHANNEL_ID = 966432292211920967  # 966432292211920967


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("--------------------------------------------")
    listen_for_key_press()  # Start listening for key presses


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("หนูไม่เข้าใจคำถามนะ?? 😣")


@client.command()
async def hello(ctx):
    await ctx.send("Hi, I'm Tiwa, Nice to meet ya! 😎")


@client.command()
async def สวัสดี(ctx):
    await ctx.send("ดีค่ะ! หนูชื่อทิวา มีอะไรรึป่าวคะ! 😎")


@client.command()
async def chat(ctx, *, question: str = None):
    if not question:
        await ctx.send("หนูไม่ได้รับคำถามนะ?? 😣")
    else:
        async with ctx.typing():
            try:
                response = tiwaChatGPT.chat_with_gpt_embedding_chat_log(question)
                await ctx.reply(response, mention_author=False)
            except Exception as e:
                await ctx.send("มีบางอย่างผิดพลาดในการรับคำตอบ 😢")
                print(f"Error: {e}")


@client.command()
async def c(ctx, *, question: str = None):
    await chat(ctx, question=question)


@client.command()
async def forget(ctx):
    tiwaChatGPT.forget()
    await ctx.send("หนูคือใคร??? ที่นี้ที่ไหน??? 🥴")


@client.command()
async def picture(ctx, *, user_input):
    if ctx.message.attachments:
        async with ctx.typing():
            response = tiwaChatGPT.chat_with_gpt_picture(
                user_input, ctx.message.attachments[0].url
            )
            await ctx.reply(response)


async def send_audio_message():
    """Record and send an audio message."""
    audio = tiwaSpeechRecognizer.record_audio()
    output_text = tiwaSpeechRecognizer.transcribe_audio(audio)
    if output_text:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            prompt = "(กาโตว์) " + output_text
            response = tiwaChatGPT.chat_with_gpt_embedding_chat_log(prompt)
            answer = f"Gateaux😎 say: {output_text}\nTiwa✨ say: {response}"
            await channel.send(answer)


def listen_for_key_press():
    """Set up key press listener to trigger audio message sending."""

    def on_key_event(e):
        # print(f"Pressed key:{e.name}")
        if e.name == "0":  # Change '0' to any key you want to use
            client.loop.create_task(send_audio_message())

    keyboard.on_press(on_key_event)


# Run the bot with the token from the environment variable
client.run(os.getenv("DISCORD_TOKEN"))
