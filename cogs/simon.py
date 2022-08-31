from discord.ext import commands
import discord
from config import token, owner_id
from static import emoji
import random
import asyncio
from cooldown import CustomCooldown as cooldown
import time

async def update_db(ctx, user_id:int, score:int):
    db = ctx.bot.db
    await db.execute(f"INSERT INTO simonleaderboard VALUES ({user_id}, {score}) ON CONFLICT DO NOTHING")
    cur = await db.execute(f"SELECT high_score FROM simonleaderboard WHERE user_id={user_id}")
    data = await cur.fetchone()
    if (data[0] < score):
        await db.execute(f"UPDATE simonleaderboard SET high_score={score} WHERE user_id={user_id}")
    await db.commit()

@commands.command()
@commands.cooldown(1, 15, commands.BucketType.user)
@commands.max_concurrency(1, commands.BucketType.user)
async def start(ctx):
    score = 0
    init_message = None

    for seq_len in range(1, 50):
        emoji_types = [emoji.RED_SQUARE, emoji.YELLOW_SQUARE, emoji.GREEN_SQUARE, emoji.BLUE_SQUARE]

        def get_sequence(num):
            returning = []
            while len(returning) < seq_len:
                apending_emoji = random.choice(emoji_types)
                if len(returning) != 0:
                    if apending_emoji != returning[-1]:
                        returning.append(apending_emoji)
                else:
                    returning.append(apending_emoji)
            return returning

        sequence = get_sequence(seq_len)

        embed=discord.Embed()
        embed.description = f"Memorize this sequence: {' '.join(sequence)}\n**DO NOT START REACTING OR IT WONT REGISTER**"

        if init_message is None: 
            init_message = await ctx.send_embed(embed)
            await ctx.add_reactions(init_message, *emoji_types)
        else: 
            await init_message.edit(embed=embed)


        await asyncio.sleep(seq_len)

        

        await init_message.edit(embed=discord.Embed(title="Now react with the correct emojis"))

        responding_sequence = []

        def check(payload):
            if payload.user_id != ctx.author.id or init_message.id != payload.message_id:
                return False
            responding_sequence.append(payload.emoji)
            return len(responding_sequence) == seq_len

        try:
            await ctx.bot.wait_for("raw_reaction", check=check, timeout=seq_len + 2)
        except asyncio.TimeoutError:
            embed=discord.Embed(title=f"YOU TOOK TOO LONG! Score: {seq_len}", color=discord.Colour.red())
            embed.set_footer(text='Play again with `simon start`')
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)
            await init_message.edit(
                embed = embed
            )
            return await update_db(ctx, ctx.author.id, seq_len)


        if [str(e) for e in responding_sequence] != sequence:
            score = seq_len
            break
    if score > 45:
        await update_db(ctx, ctx.author.id, score)
        return await ctx.send(f"WOW that is a really good score! Score: {score}")
    await init_message.edit(
        embed=discord.Embed(title=f"Incorrect sequence. Total score: {score}")
            .set_footer(text='Play again with `simon start`')
            .set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)
    )
    await update_db(ctx, ctx.author.id, score)
###########################################################
@commands.command()
async def ping(ctx):
        start = time.perf_counter()
        msg = await ctx.send("pinging...")
        end = time.perf_counter()
        http_ping = (end-start)*1000

        websocket_ping = ctx.bot.latency*1000

        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        async with ctx.bot.db.execute(query) as cur:
            row = await cur.fetchall()
        a = [i[0] for i in row]
        start = time.perf_counter()
        for name in a:
            query = f"SELECT * FROM {name}"
            async with ctx.bot.db.execute(query):
                end = time.perf_counter()

        sql_ping = (end-start)*1000

        await msg.edit(content = f"**WEBSOCKET:** {round(websocket_ping, 2)}ms\n**TYPING:** {round(http_ping, 2)}ms\n**DATABASE:** {round(sql_ping, 3)}ms")

def setup(bot):
    bot.add_command(start)
    bot.add_command(ping)
