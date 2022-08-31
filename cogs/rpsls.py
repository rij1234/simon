from discord.ext import commands
import discord
import asyncio
from cooldown import CustomCooldown as cooldown

@commands.command()
async def rpsls(ctx, opponent: discord.Member):
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

        async def check_winner(self, author_response, opp_response, interaction):

            if author_response == opp_response:
                return await interaction.response.edit_message(content=f"Both players chose {author_response}. TIE", view=self)
            wins = [
                ['scissors', 'cut', 'paper'], 
                ['paper', 'covers', 'rock'], 
                ['rock', 'crushes', 'lizard'], 
                ['lizard', 'poisons', 'spock'], 
                ['spock', 'smashes', 'scissors'], 
                ['scissors', 'decapitates', 'lizard'], 
                ['lizard', 'eats', 'paper'], 
                ['paper', 'disproves', 'spock'], 
                ['spock', 'vaporizes', 'rock'], 
                ['rock', 'crushes', 'scissors']
            ]

            for w in wins:
                if author_response == w[0] and opp_response == w[2]:
                    for button in self.children:
                        if isinstance(button, discord.ui.Button):
                            button.disabled = True
                    self.stop()
                    return await interaction.response.edit_message(content=f"{w[0]} {w[1]} {w[2]}. {ctx.author.mention} beat {opponent.mention}", view=self)

                elif opp_response == w[0] and author_response == w[2]:
                    for button in self.children:
                        if isinstance(button, discord.ui.Button):
                            button.disabled = True
                    self.stop()
                    return await interaction.response.edit_message(content=f"{w[0]} {w[1]} {w[2]}. {opponent.mention} beat {ctx.author.mention}", view=self)


        async def button_pressed(self, button, interaction):
            if interaction.user.id == ctx.author.id:
                self.ctx_answer = button
            elif interaction.user.id == opponent.id:
                self.opponent_answer = button 

            if self.ctx_answer and self.opponent_answer:
                if not self.is_ended:
                    await self.check_winner(self.ctx_answer, self.opponent_answer, interaction)


        async def on_timeout(self):
            for button in self.children:
                if isinstance(button, discord.ui.Button):
                    button.disabled = True
            await ctx.reply(content=f"{ctx.author.mention} sorry, they didn't repond in time")

        @discord.ui.button(style=discord.ButtonStyle.primary, label="rock", emoji = "\U0001faa8")
        async def rock(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="paper", emoji = "\U0001f4f0")
        async def paper(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="scissors", emoji = "\U00002702")
        async def scissors(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="lizard", emoji = "\U0001f98e")
        async def lizard(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="spock", emoji = "\U0001f596")
        async def spock(self, button, interaction):
            await self.button_pressed(button.label, interaction)

    view = View(timeout=20)
    msg = await ctx.send(content="Rock Paper Scissors", view = view)

def setup(bot):
	bot.add_command(rpsls)