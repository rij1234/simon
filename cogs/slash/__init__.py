from discord.ext import commands
import discord

class Slash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_interaction(self, interaction):
		if interaction.type is discord.InteractionType.application_command: #checks if its a slash command response
			pass


def setup(bot):
	bot.add_cog(Slash(bot))