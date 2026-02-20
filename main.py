# ローカルLLMとイチャイチャするためのDiscordBot
# 2026-02-12: RenMikekado

import os
import tomllib
import discord
from discord.ext import commands
from openai import AsyncOpenAI

setting_path = "./settings.toml"
if not os.path.isfile(setting_path):
    setting_path = "./default_settings.toml"

with open(setting_path, "rb") as f:
    settings = tomllib.load(f)
    token = settings["token"]
    model = settings["model"]
    temperature = settings["temperature"]
    system_prompt = settings["system_prompt"]

client = AsyncOpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"assistant logined as: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        async with message.channel.typing():
            history = []
            async for msg in message.channel.history(limit = 32):
                if not msg.content:
                    continue

            role = "assistant" if msg.author == bot.user else "user"
            name = msg.author.display_name.replace(" ", "_").replace(".", "-")
            history.append({
                "role": role,
                "name": name,
                "content": msg.content
            })
        
            history.append({
                "role": "system",
                "name": "System-prompt",
                "content": system_prompt
            })

            history.reverse()

            print(history)

            response = await client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=history,
            )

            await message.channel.send(response.choices[0].message.content)

bot.run(token)