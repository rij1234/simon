from discord.ext import commands
import discord
import asyncio
from cooldown import CustomCooldown as cooldown

@commands.command()
@commands.cooldown(1, 20, commands.BucketType.user)
@commands.max_concurrency(1, commands.BucketType.channel)
async def jones(ctx, opponent: discord.Member):
    if opponent.bot:
        return await ctx.reply("Can't challenge a bot")
    if ctx.author == opponent:
        return await ctx.send("Can't challenge urself")
    class View(discord.ui.View):
        def __init__(self, *args, **kwargs):
            self.ctx_answer = None
            self.opponent_answer = None
            self.is_ended = False
            self.ctx_has_ammo = False
            self.opponent_has_ammo = False
            super().__init__(*args, **kwargs)

        async def do_move(self, interaction):
            pass

        async def button_pressed(self, name, interaction):
            if interaction.user == ctx.author and self.ctx_answer is None:
                self.ctx_answer = name
            if self.ctx_answer is not None and self.opponent_answer is not None:
                await do_move(interaction)

        async def opponent_button_pressed(self, name, interaction):
            if interaction.user == opponent and self.opponent_answer is None:
                self.opponent_answer = name
            if self.ctx_answer is not None and self.opponent_answer is not None:
                await do_move(interaction)

        @discord.ui.button(style=discord.ButtonStyle.red, label=ctx.author.name + ":", disabled = True)
        async def o(self, button, interaction):
            pass

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Reload")
        async def reload(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Shield")
        async def shield(self, button, interaction):
            await self.button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Shoot")
        async def shoot(self, button, interaction):
            await self.button_pressed(button.label, interaction)


        @discord.ui.button(style=discord.ButtonStyle.red, label=opponent.name + ":", disabled = True, group = 1)
        async def _o(self, button, interaction):
            pass

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Reload", group = 1)
        async def reload_o(self, button, interaction):
            await self.opponent_button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Shield", group = 1)
        async def shield_o(self, button, interaction):
            await self.opponent_button_pressed(button.label, interaction)

        @discord.ui.button(style=discord.ButtonStyle.primary, label="Shoot", group = 1)
        async def shoot_o(self, button, interaction):
            await self.opponent_button_pressed(button.label, interaction)

    msg = await ctx.send(content="Indiana Jones", view = View(timeout=10))

def setup(bot):
	bot.add_command(jones)
