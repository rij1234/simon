from discord.ext import commands
import discord
import asyncio
from cooldown import CustomCooldown as cooldown

def is_win(board_data):
	if (board_data[0][0] == board_data[0][1] == board_data[0][2] != '⬜') or (board_data[1][0] == board_data[1][1] == board_data[1][2] != '⬜') or (board_data[2][0] == board_data[2][1] == board_data[2][2] != '⬜'):
		return True
	if (board_data[0][0] == board_data[1][0] == board_data[2][0] != '⬜') or (board_data[0][1] == board_data[1][1] == board_data[2][1] != '⬜') or (board_data[0][2] == board_data[1][2] == board_data[2][2] != '⬜'):
		return True
	if (board_data[0][0] == board_data[1][1] == board_data[2][2] != '⬜') or (board_data[0][2] == board_data[1][1] == board_data[2][0]!= '⬜'):
		return True
	return False

@commands.command()
@commands.check(cooldown(1, 10, commands.BucketType.user))
@commands.max_concurrency(1, commands.BucketType.channel)
async def tictactoe(ctx, opponent: discord.User):
	if opponent.bot == True:
		return await ctx.send("Cannot challenge a bot")
	if opponent.id == ctx.author.id:
		return await ctx.send("cannot challenge urself")
	current_player = ctx.author
	board_data = [['⬜', '⬜', '⬜'], ['⬜', '⬜', '⬜'], ['⬜', '⬜', '⬜']]
	def get_board():
		return f"""
⬛1️⃣2️⃣3️⃣
🇦{"".join(board_data[0])}  ❌ {ctx.author.mention}{'⬅'if current_player == ctx.author else ''}
🇧{"".join(board_data[1])}  🅾️ {opponent.mention}{'⬅' if current_player == opponent else ''}
🇨{"".join(board_data[2])}
Must be format: a1, b1, c2, etc. 
		"""
	board = await ctx.send(get_board())
	turn = 0
	while True:
		def check(m):
			return m.author.id == current_player.id
		try:
			usr_resp = await ctx.bot.wait_for("message", check=check, timeout=10)
		except asyncio.TimeoutError:
			continue
		if (len(usr_resp.content) != 2) or (usr_resp.content[0].lower() not in ['a', 'b', 'c']) or (usr_resp.content[1] not in ['1', '2', '3']):
			# await usr_resp.reply("Must be format: a1, b1, c2, etc. **TRY AGAIN YOU NINCOMPOOP**")
			continue
		let, num = usr_resp.content[0], int(usr_resp.content[1])

		if let.lower() == "a":
			let = 1
		elif let.lower() == "b":
			let = 2
		elif let.lower() == "c":
			let = 3

		if current_player.id == ctx.author.id:
			if board_data[let-1][num-1] != "⬜":
				await usr_resp.reply("That spot is taken. **TRY AGAIN YOU NINCOMPOOP**")
				continue
			board_data[let-1][num-1] = (":x:")
			current_player = opponent
		else:
			if board_data[let-1][num-1] != "⬜":
				await usr_resp.reply("That spot is taken. **TRY AGAIN YOU NINCOMPOOP**")
				continue
			board_data[let-1][num-1] = (":o2:")
			current_player = ctx.author
		# await board.edit(content=get_board())
		await ctx.send(get_board())
		turn += 1
		if turn == 9:
			return await ctx.send("TIE")
		if is_win(board_data):
			if current_player.id == ctx.author.id:
				return await ctx.send(f"{opponent} won")
			else:
				return await ctx.send(f"{ctx.author} won")
		if board_data[0] == board_data[1] == board_data[2]:
			return await ctx.send("TIE")









from discord.ext import commands
import discord

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', group=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                assert isinstance(child, discord.ui.Button) # just to shut up the linter
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

@commands.command()
async def tic(ctx: commands.Context):
    await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())










def setup(bot):
    bot.add_command(tictactoe)
    bot.add_command(tic)
