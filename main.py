from config import token, owner_id, logger_webhook_url
from cooldown import CustomCooldown as cooldown
from discord.ext import commands, tasks
from prettytable import PrettyTable
from discord.ext import menus
from static import emoji
import help_command
import aiosqlite
import importlib
import traceback
import asyncio
import asyncpg
import aiohttp
import random
import json
import time
import sys
###########################################################
import discord
###########################################################
class BotContext(commands.Context):
    async def send_embed(self, embed:discord.Embed, **kwargs):
        return await self.send(embed=embed, **kwargs)
    async def add_reactions(self, message, *emojis):
        for emoji in emojis:
            await message.add_reaction(emoji)
    async def send_auto_paginate(self, content, limit=2000, **kwargs):
        paginator = commands.Paginator()
        for i in content.split("\n"):
            paginator.add_line(i)
        for page in paginator.pages:
            await self.send(page)
    async def send_paginate_menu(self, rows, per_page, begin="```", end="```"):
        class MainMenu(menus.ListPageSource):
            def __init__(self, rows, per_page, begin="```", end="```", **kwargs):
                self.begin = begin
                self.end = end
                super().__init__(rows, per_page=per_page)

            async def format_page(self, menu, entries):
                offset = menu.current_page * self.per_page
                return f"{self.begin}" +  '\n'.join(f'{v}' for i, v in enumerate(entries, start=offset)) + f"{self.end}"

        pages = menus.MenuPages(source=MainMenu(rows=rows, per_page=per_page, begin=begin, end=end), clear_reactions_after=True)
        await pages.start(self)
###########################################################
###########################################################
intents = discord.Intents.none()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.members = True
###########################################################
class BotClass(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        self.leaderboard_cache = {}
        self.full_traceback_enabled = False
        self.prefixes = {}
        super().__init__(*args, **kwargs)

    def toggle_traceback(self):
        if self.full_traceback_enabled:
            self.full_traceback_enabled = False
        else:
            self.full_traceback_enabled = True

    async def load_all_prefixes(self):
        d = await self.db.execute("SELECT * FROM prefixes")
        d = dict(await d.fetchall())
        self.prefixes = d
        return d

    async def get_context(self, message, *, cls=BotContext):
        return await super().get_context(message, cls=cls)

    @tasks.loop(minutes=5)
    async def update_status(self):
            await self.change_presence(activity=discord.Game(name=f"'simon help' | VERIFIED!! | {len(self.guilds)}/1000 servers"))

    async def on_ready(self):
        print("bot ready")
        self.update_status.start()

    async def on_message(self, message):
        if message.content in [f"<@{self.user.id}>", f"<@!{self.user.id}>"]:
            prefixes = await self.command_prefix(self, message)
            text = '\n'.join(prefixes)
            return await message.reply(f"""Prefixes: \n```{text}```""")
        await self.process_commands(message)

    async def on_raw_reaction_add(self, payload):
        self.dispatch("raw_reaction", payload)

    async def on_raw_reaction_remove(self, payload):
        self.dispatch("raw_reaction", payload)

    async def _on_guild_remove(self, guild):
        name = guild.name
        id = guild.id
        async with aiohttp.ClientSession() as session:
            url = logger_webhook_url
            webhook = discord.Webhook.from_url(url, session=session)
            embed = discord.Embed(title=f"{guild.name} has removed the bot")
            embed.description = f"Bot Guild Count: {len(self.guilds)}"
            embed.set_thumbnail(url=str(guild.icon.url))
            embed.color = 0xe74c3c
            await webhook.send(username="Simon Game", avatar_url=str(self.user.avatar.url), embed=embed)


    async def on_guild_remove(self, guild):
        # return await on_guild_remove(guild)
        name = guild.name
        id = guild.id
        data = {
            "embeds": [
                {
                    "username":"Simon Game",
                    "avatar_url":str(self.user.avatar.url),
                    "color":0xe74c3c,
                    "title": f"{guild.name} has removed the bot",
                    "thumbnail":{
                        "url":str(guild.icon.url)
                    },
                    "description": f"Bot Guild Count: {len(self.guilds)}"
                }
            ]
        }
        url = logger_webhook_url
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            d = await session.post(url, data=json.dumps(data))
            return await d.text()

    async def _on_guild_join(self, guild):
        name = guild.name
        id = guild.id
        async with aiohttp.ClientSession() as session:
            pass

    async def on_guild_join(self, guild):
        name = guild.name
        id = guild.id
        data = {
            "embeds": [
                {
                "username":"Simon Game", 
                "avatar_url":str(self.user.avatar.url),
                "color":0x2ecc71,
                "title": f"{guild.name} has added the bot",
                "thumbnail":{
                    "url":str(guild.icon.url)
                },
                "description": f"Bot Guild Count: {len(self.guilds)}"
                }
            ]
        }
        url = logger_webhook_url
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            d = await session.post(url, data=json.dumps(data))
            return await d.text()
    async def on_command_error(self, ctx, error):
        if not ctx.guild.me.guild_permissions.embed_links:
            return await ctx.send("An error occured, but i must have 'embed links' permission. Please give it to me")
        command = ctx.command
        if (await self.is_owner(ctx.author)) and self.full_traceback_enabled:
            etype = type(error)
            trace = error.__traceback__
            lines = traceback.format_exception(etype, error, trace)
            text = ''.join(lines)
            return await ctx.send_embed(discord.Embed(title="Error", color=discord.Colour.red(), description=text))
        if isinstance(error, asyncio.TimeoutError):
            return await ctx.send("You took too long, and therefore the game timed out and ended.")
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply(f"""```simon ({command.name}{"|" if (len(command.aliases) != 0)  else ""}{"|".join(command.aliases)}) {command.signature}\n\n{error}```""")
        await ctx.send(embed = discord.Embed(title="Error", color=discord.Colour.red(), description=str(error)))

    def run(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        async def connect_to_db():
            self.db = await aiosqlite.connect("database.db")
            print("Connected to database")
        loop.run_until_complete(connect_to_db())
        loop.run_until_complete(self.load_all_prefixes())
        super().run(*args, **kwargs)

    # async def run(self, *args, **kwargs):
    
    #     self.db = await aiosqlite.connect("database.db")
    #     print("connected to database")

    #     await self.load_all_prefixes()
    #     print("prefixes loaded")
    
    #     await super().start(*args, **kwargs)
    #     Print("bot started")

###########################################################
async def command_prefix(bot, msg):
    """CREATE TABLE prefixes (userid bigint unique, prefix varchar(5))"""
    base = ["Simon ", "simon "]
    if msg.guild is None:
        return base
    add_on = bot.prefixes.get(msg.author.id, None)
    if add_on is not None:
        base.append(add_on)
    return base
###########################################################
bot = BotClass(
    command_prefix=command_prefix, 
    owner_id=owner_id, 
    intents=intents,
)
bot.help_command = help_command.HelpCommand()
###########################################################
class Games_Solo(commands.Cog, name="Solo Games"):
    def __init__(self, bot):
        self.bot = bot
class Games_1v1(commands.Cog, name="1v1 Games"):
    def __init__(self, bot):
        self.bot = bot
bot.add_cog(Games_Solo(bot))
bot.add_cog(Games_1v1(bot))
###########################################################
@bot.command(aliases=['reload', 'restart', 'reset'], hidden=True)
@commands.is_owner()
async def _reload(ctx, arg):
    bot.reload_extension(f"cogs.{arg}")
    await ctx.send(f"Reloaded: {arg}")

@bot.command(aliases=['unload', 'stop'], hidden=True)
@commands.is_owner()
async def _stop(ctx, arg):
    bot.unload_extension(f"cogs.{arg}")
    await ctx.send(f"Unloaded: {arg}")

@bot.command(aliases=['load'], hidden=True)
@commands.is_owner()
async def _load(ctx, arg):
    bot.load_extension(f"cogs.{arg}")
    await ctx.send(f"Loaded: {arg}")
###########################################################
@bot.command(aliases=["rhelp"], hidden=True)
@commands.is_owner()
async def reloadhelp(ctx):
    importlib.reload(__import__("help_command"))
    bot.help_command = __import__("help_command").HelpCommand()
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
###########################################################
@bot.command(name="about", aliases=["info"])
async def _about(ctx):
    embed = discord.Embed(title=bot.user.name)
    embed.add_field(name="Owner", value=str(bot.get_user(bot.owner_id)))
    embed.add_field(name="Python", value=sys.version)
    embed.add_field(name="Made with", value="discord.py")
    embed.add_field(name="DPY version", value=__import__("jishaku").modules.package_version("discord.py")) # value=discord.__version__)
    embed.add_field(name="Guilds", value=len(bot.guilds))
    embed.add_field(name="approx. Users", value=len(bot.users))
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)
###########################################################
async def update_prefix(bot, user_id, prefix: str):
        await bot.db.execute(f"REPLACE INTO prefixes (userid, prefix) VALUES ({user_id}, '{prefix}')")
        await bot.db.commit()
        bot.prefixes[user_id] = prefix
        return prefix

@bot.command(hidden = True)
async def setprefix(ctx, *, prefix: str):
    if len(prefix) > 5:
        return await ctx.send("Prefix must be less than 6 characters")
    p = await update_prefix(ctx.bot, ctx.author.id, prefix)
    await ctx.send(f"Prefix is now `{p}`. \n **THIS IS A USER SPECIFIC PREFIX")

@bot.command(hidden = True)
async def prefix(ctx):
    p = await command_prefix(ctx.bot, ctx.message)
    await ctx.send(f"Prefix is `{p[-1]}`. \n **THIS IS A USER SPECIFIC PREFIX")
###########################################################
bot.load_extension("cogs.simon")
bot.load_extension("cogs.tictactoe")
bot.load_extension("cogs.connect4")
bot.load_extension("cogs.dbl")
bot.load_extension("cogs.leaderboard")
bot.load_extension("cogs.rps")
bot.load_extension("cogs.rpsls")
bot.load_extension("cogs.ipc")
bot.load_extension("jishaku")
bot.load_extension("eval")
###########################################################
bot.run(token)
