from discord.ext import commands
import discord
import asyncio
from cooldown import CustomCooldown as cooldown

@commands.command()
async def rps(ctx, opponent: discord.Member):
    if opponent.bot:
        return await ctx.reply("Can't challenge a bot")
    if ctx.author == opponent:
        return await ctx.send("Can't challenge urself")
    class View(discord.ui.View):
        def __init__(self, *args, **kwargs):
            self.ctx_answer = None
            self.opponent_answer = None
            self.is_ended = False
            super().__init__(*args, **kwargs)

        async def interaction_check(self, ineraction):
            if interaction.user.id != ctx.author.id  and interaction.user.id != opponent.id:
                return

        async def button_pressed(self, button, interaction):
            if interaction.user.id == ctx.author.id:
                self.ctx_answer = button
            elif interaction.user.id == opponent.id:
                self.opponent_answer = button 

            if self.ctx_answer and self.opponent_answer:

                if not self.is_ended:
                    for button in self.children:
                        if isinstance(button, discord.ui.Button):
                            button.disabled = True
                    await interaction.response.edit_message(content=f"{ctx.author.mention} did {self.ctx_answer}\n{opponent.mention} did {self.opponent_answer}", view=self)
                    self.is_ended = True
                    self.stop()

        async def on_timeout(self):
            for button in self.children:
                if isinstance(button, discord.ui.Button):
                    button.disabled = True
            await ctx.reply(content=f"{ctx.author.mention} sorry, they didn't repond in time")

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Rock", emoji = "\U0001faa8")
        async def rock(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Paper", emoji = "\U0001f4f0")
        async def paper(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Scissors", emoji = "\U00002702")
        async def scissors(self, button, interaction):
            await self.button_pressed(button.label, interaction)

    view = View(timeout=10)
    msg = await ctx.send(content="Rock Paper Scissors (times out in 10 seconds!)", view = view)

def setup(bot):
	bot.add_command(rps)