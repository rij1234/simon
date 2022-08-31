import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):
    commands = {
            "Solo Games": {
                "commands": [
                    {
                        "command": "start",
                        "description": "- Classic simon memory game"
                    },
                ],
            },
            "1v1 Games": {
                "commands":[
                    {
                        "command": "tictactoe <@opponent>",
                        "description": "Tictactoe, respond in format `a1`, `b2`"
                    },
                    {
                        "command": "connect4 <@opponent>",
                        "description": "Classic connect4, get 4 in a row!"
                    },
                    {
                        "command": "rps <@opponent>",
                        "description": "Rock paper scissors with discord buttons"
                    },
                    {
                        "command": "rpsls <@opponent>",
                        "description": "Rock paper scissors lizard spock from Big Bang Theory. [Diagram](https://aws1.discourse-cdn.com/codecademy/original/5X/1/e/9/a/1e9ae22826a47a2d2e9f0e8f0f0cdf21a8479715.jpeg)"
                    },
                ],
            },
            "Misc": {
                "commands":[
                    {
                        "command": "glb",
                        "description": "Leaderboard for your server in `simon start`"
                    },
                    {
                        "command": "setprefix <prefix>",
                        "description": "- sets the prefix to whatever you want it to be **USER SPECIFIC**"
                    },
                    {
                        "command": "simon prefix",
                        "description": "- gets your prefix"
                    },
                ],
            },
        }

    async def send_bot_help(self, mapping):
        context = self.context


        start_embed=discord.Embed(title="Simon Game", color = discord.Colour.green())
        start_embed.description = """
This is a discord bot with many fun games, specifically those that are fun! The focus on this is quality rather than quantity, so we will continue to make more awesome games.  
**WARNING:** This help command may not work on mobile due to buttons being defective
        """

        class ButtonClass(discord.ui.Button):
            def __init__(self, group_name, commands, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.embed = discord.Embed(title=group_name, color = discord.Colour.green())
                for c in commands:
                    self.embed.add_field(name= context.clean_prefix + c["command"], value=c["description"] or "** **", inline=False)

            async def callback(self, interaction):
                if interaction.user.id != context.author.id:
                    return await interaction.response.send_message(content="hey! this is not your help command! type `simon help` to use it yourself", ephemeral=True)
                await interaction.response.edit_message(content="** **", embed=self.embed)
        
        class EndButton(discord.ui.Button):
            async def callback(self, interaction):
                if interaction.user.id != context.author.id:
                    return await interaction.response.send_message("This is not your help command!", ephemeral= True)
                for button in self.view.children:
                    if isinstance(button, discord.ui.Button) and button.url is None:
                        button.disabled = True
                await interaction.response.edit_message(content="** **", embed=discord.Embed(title="Command Ended", color = discord.Colour.red()), view=self.view)
                self.view.stop()

        class myView(discord.ui.View):
            pass
           

        view = myView(timeout=180)

        for k in self.commands:
            view.add_item(
                ButtonClass(k, self.commands[k]["commands"], label=k, style=discord.ButtonStyle.blurple, group=2)
            )

        view.add_item(EndButton(style=discord.ButtonStyle.danger, emoji="\U0001f6d1", group=2))

        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary, 
            label="Invite Link", 
            url = "https://discord.com/oauth2/authorize?client_id=825236871377453066&scope=applications.commands%20bot&permissions=1140968528", 
            group=3)
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.primary, 
                label="Top.gg", 
                url = "https://top.gg/bot/825236871377453066"
                , group=3
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.primary, 
                label="Website", 
                url = "https://simon.rjson.dev", 
                group=3
            )
        )


        channel = self.get_destination()
        await channel.send(embed=start_embed, view=view)






























class aHelpCommand(commands.HelpCommand):
	def get_command_signature(self, command):
		return f""" - simon {command.name}"""

	async def send_bot_help(self, mapping):
		help_embed = discord.Embed(title="Commands")
		help_embed.add_field(name="Solo Games", value=f"""
			__{self.context.clean_prefix}start__ - Classic simon memory game
		""", inline=False)
		help_embed.add_field(name="1v1 Games", value=f"""
			__{self.context.clean_prefix}tictactoe <@opponent>__
			__{self.context.clean_prefix}connect4 <@opponent>__
		""", inline=False)
		help_embed.add_field(name="Misc", value=f"""
			__{self.context.clean_prefix}glb__
			  - Leaderboard for your server in `simon start`
		""", inline=False)
		help_embed.add_field(name="Prefix (user specific)", value=f"""
			__{self.context.clean_prefix}setprefix <prefix>__
			  - sets the prefix to whatever you want it to be
			__{self.context.clean_prefix}prefix__
			  - gets your prefix
		""", inline=False)
		# for cog, commands iname="n mapping.items():
		# 	if cog is not None:
		# 		command_formatted = [self.get_command_signature(c) for c in self.context.bot.commands 
		# 			    if getattr(c.cog, "qualified_name", "Unnamed") == cog.qualified_name]
		# 		if command_formatted:
		# 			help_embed.add_field(
		# 				name=cog.qualified_name, 
		# 				value="\n".join(command_formatted),
		# 				inline=False
		# 			)
		# 		# help_embed.add_field(name=str(cog.qualified_name), value=str(len(commands)))

		channel = self.get_destination()

		await channel.send(embed=help_embed)
