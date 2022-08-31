from discord.ext import commands
import discord
from config import token, owner_id
from static import emoji
import random
import asyncio
from cooldown import CustomCooldown as cooldown

@commands.command()
async def reaction(ctx):
	class View(discord.ui.View):
		sleep_time = random.random() * 20
		pass

	view = View(timeout=20)
	for i in range(25):
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.grey, label="Button", disabled=True))

	await ctx.send("View", view=view)

def setup(bot):
	bot.add_command(reaction)