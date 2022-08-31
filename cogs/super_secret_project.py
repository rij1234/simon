import discord
from discord.ext import commands
import asyncio 

@commands.command()
async def secret(ctx):
	if ctx.author.id != ctx.bot.owner_id:
		return await ctx.send("Bruh did you not read the title of the command")

	await ctx.send("DMing message")
	await asyncio.sleep(2)
	await ctx.send("Success!")

def setup(bot):
	bot.add_command(secret)