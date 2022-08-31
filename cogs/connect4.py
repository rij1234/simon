from discord.ext import commands
import discord
from config import token, owner_id
from static import emoji
import random
import asyncio
from cooldown import CustomCooldown as cooldown

async def is_win(board):
	boardwidth = len(board)
	boardheight = len(board[0])


	# check horizontal spaces
	for y in range(boardheight):
		for x in range(boardwidth - 3):
			if board[x][y] == board[x+1][y] == board[x+2][y] == board[x+3][y] != emoji.WHITE_SQUARE:
				return True



    #check vertical spaces
	for x in range(boardwidth):
		for y in range(boardheight - 3):
			if board[x][y] == board[x][y+1] == board[x][y+2] == board[x][y+3] != emoji.WHITE_SQUARE:
				return True

	#check / diagonal spaces
	for x in range(boardwidth - 3):
		for y in range(3, boardheight):
			if board[x][y] == board[x+1][y-1] == board[x+2][y-2] == board[x+3][y-3] != emoji.WHITE_SQUARE:
				return True

	#check \ diagonal spaces
	for x in range(boardwidth - 3):
		for y in range(boardheight - 3):
			if board[x][y] == board[x+1][y+1] == board[x+2][y+2] == board[x+3][y+3] != emoji.WHITE_SQUARE:
				return True
	return False


@commands.command(description="Classic 1v1 connect4")
@commands.check(cooldown(1, 10, commands.BucketType.user))
@commands.max_concurrency(1, commands.BucketType.user)
@commands.max_concurrency(1, commands.BucketType.channel)
async def connect4(ctx, opponent: discord.Member):
	if opponent.bot:
		return await ctx.reply("Can't challenge a bot")
	if ctx.author == opponent:
		return await ctx.send("Can't challenge urself")
	player1 = ctx.author
	player2 = opponent
	current_player = ctx.author
	boarddata = [
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE], 
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE], 
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE], 
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE], 
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE], 
		[emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE, emoji.WHITE_SQUARE]
	]
	def getboard():
		return f"""
{"".join(boarddata[0])}
{"".join(boarddata[1])} {emoji.RED_CIRCLE} {str(ctx.author)}
{"".join(boarddata[2])} {emoji.YELLOW_CIRCLE} {str(opponent)}
{"".join(boarddata[3])}
{"".join(boarddata[4])}
{"".join(boarddata[5])}
0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣
Give a number from 0-6
		"""
	init_msg = await ctx.send(getboard())
	await init_msg.add_reaction("0️⃣")
	await init_msg.add_reaction("1️⃣")
	await init_msg.add_reaction("2️⃣")
	await init_msg.add_reaction("3️⃣")
	await init_msg.add_reaction("4️⃣")
	await init_msg.add_reaction("5️⃣")
	await init_msg.add_reaction("6️⃣")
	while True:
		emojis = {"0️⃣": 0, "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6}
		payload = await ctx.bot.wait_for("raw_reaction", check = lambda m: m.user_id == current_player.id and str(m.emoji) in emojis)
		column_num = emojis[str(payload.emoji)]

		for num, i in enumerate(boarddata[::-1]):
			if boarddata[5 - num][column_num] == emoji.WHITE_SQUARE:
				if current_player == player1:
					boarddata[5 - num][column_num] = emoji.RED_CIRCLE
				elif current_player == player2:
					boarddata[5 - num][column_num] = emoji.YELLOW_CIRCLE
				break

		await init_msg.edit(content=getboard())

		if await is_win(boarddata):
			return await ctx.send(f"{current_player} won the game {player1.mention} {player2.mention}")

		if current_player == player1:
			current_player = player2
		elif current_player == player2:
			current_player = player1


def setup(bot):
    bot.add_command(connect4)