from discord.ext import commands, tasks
import discord
from prettytable import PrettyTable
import datetime

@commands.command()
async def highscore(ctx, user:discord.User = None):

    db = ctx.bot.db
    user_id = ctx.author.id

    if user is None:
        user = ctx.author

    await db.execute(f"INSERT INTO simonleaderboard VALUES ({user_id}, 0) ON CONFLICT DO NOTHING")
    cur = await db.execute(f"SELECT high_score FROM simonleaderboard WHERE user_id={user_id}")
    data = await cur.fetchone()

    await ctx.send_embed(discord.Embed(title=f"Your high score in simon game: {data[0]}", color=discord.Colour.blue()))
 
@commands.command(name="glb")
async def guildleaderboard(ctx):
    table = PrettyTable(["Name", "High Score"])
    data = await(
        await ctx.bot.db.execute(
            f"SELECT * FROM simonleaderboard WHERE user_id IN ({', '.join([str(m.id) for m in ctx.guild.members])}) ORDER BY high_score DESC LIMIT 30"
        )
    ).fetchall()

    for user, high_score in data:
        table.add_row([str(ctx.bot.get_user(int(user))).encode("ascii", "ignore").decode("ascii"), high_score])

    await ctx.send_paginate_menu(
        rows=str(table).split("\n"),
        per_page=10
    )


@commands.command()
@commands.is_owner()
async def leaderboard(ctx):

    table = PrettyTable(["Place", "Name", "High Score"])

    for current_placement, user, high_score in ctx.bot.leaderboard_cache["global"]:
        table.add_row([current_placement, str(user).encode("ascii", "ignore").decode("ascii"), high_score])

    await ctx.send_paginate_menu(
        rows=str(table).split("\n"), 
        per_page=15, 
        begin="**GLOBAL LEADERBOARD:** ```\n", 
        end=f"\n``` Last Updated {datetime.datetime.utcnow() - ctx.bot.leaderboard_cache['global-last-updated']}"
    )


@tasks.loop(minutes=10)
async def update_global_simon_leaderboard(bot):
    await bot.wait_until_ready()
    bot.leaderboard_cache["global"] = []
    data = await (await bot.db.execute("SELECT * FROM simonleaderboard ORDER BY high_score DESC")).fetchall()
    fulldata = []

    current_placement = 1
    for user, high_score in data:
        user_obj = bot.get_user(int(user)) # needs members intent
        fulldata.append([current_placement, user_obj, high_score])
        current_placement += 1

    bot.leaderboard_cache["global"] = fulldata
    bot.leaderboard_cache["global-last-updated"] = datetime.datetime.utcnow()


def setup(bot):
    bot.add_command(highscore)
    bot.add_command(leaderboard)
    bot.add_command(guildleaderboard)
    update_global_simon_leaderboard.start(bot)

def teardown(bot):
    update_global_simon_leaderboard.stop()
    bot.remove_command(highscore)
    bot.remove_command(leaderboard)
    bot.remove_command(guildleaderboard)