import random
import discord
from discord.ext import commands,tasks
from discord import app_commands
import logging
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="!!",intents=discord.Intents.all(),application_id=int(os.getenv("BOT_ID")))


@bot.event
async def on_ready(): 
    print("Sincronizado, basta utilizar!")
    

class SubButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.timeout=399

        meugithub= discord.ui.Button(label="Desenvolvido por Paulo Alarico",url="https://wwwlg8t,q,q ")
        self.add_item(meugithub)


@bot.command()
@commands.is_owner() 
async def sync(ctx,guild=None):
    if guild == None:
        await bot.tree.sync()
    else:
        await bot.tree.sync(guild=discord.Object(id=int(guild)))
    await ctx.send("**SINCRONIZADO&",view=SubButton())

async def main():
    async with bot:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

        
        TOKEN = os.getenv("DISCORD_TOKEN")
        await bot.start(TOKEN)

asyncio.run(main())

