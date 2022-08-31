import discord
from discord.ext import commands
from random import randint

class BoardPiece:
    hit = 1
    miss = 2
    miss_unchecked = "\N{LARGE BLUE SQUARE}"
    hit_unchecked = "\N{LARGE BLUE SQUARE}"

class Button(discord.ui.Button):
    def __init__(self, is_hit,  *args, **kwargs):
        super().__init__(label = "X", *args, **kwargs)
        self.is_hit = is_hit
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        if self.is_hit:
            self.label = "\U0001f534"
            self.view.hits_found += 1
        else:
            self.label = "\N{LARGE BLUE SQUARE}"

        if self.view.hits_found >= self.view.total_hits:
                for button in self.view.children:
                    button.disabled = True
                return await interaction.response.edit_message(content="welp, ya found all", view=self.view)

        await interaction.response.edit_message(content="So, uh, here is board?" , view=self.view)


class View(discord.ui.View):
    def __init__(self, board, authorized_user, *args, **kwargs):
        self.board = board
        self.total_hits = 0
        self.hits_found = 0
        self.authorized_user = authorized_user
        super().__init__(*args, **kwargs)
        for i in range(5):
            for j in range(5):
                is_hit = self.check_position(i, j)
                if is_hit:
                    self.total_hits += 1
                self.add_item(Button(style=discord.ButtonStyle.secondary, is_hit=is_hit))

    async def interaction_check(self, interaction):
        return interaction.user.id == self.authorized_user.id


    def check_position(self, x, y) -> bool:
        board_item = self.board[x][y]
        if board_item == "\N{LARGE BLUE SQUARE}":
            return False
        else:
            return True



@commands.command()
async def battleship(ctx):
    blank_emoji = "\N{LARGE BLUE SQUARE}"
    vert_ships = [4]
    hori_ships = [2, 3]
    def get_board() -> list:
        board = [
            [blank_emoji for i in range(5)]
        for i in range(5)]

        ship_coords = []

        for i in vert_ships:
            pos = (randint(0, len(board) - i), randint(0, len(board)- 1))
            board[pos[0]][pos[1]] = "\U0001f534"
            for j in range(i):
                board[pos[0] + j][pos[1]] = "\U0001f534"

        for i in vert_ships:
            pos = (randint(0, len(board) - i), randint(0, len(board)- 1))
            board[pos[1]][pos[0]] = "\U0001f534"
            for j in range(i):
                board[pos[1]][pos[0] + j] = "\U0001f534"
        return board


    board = get_board()

    board_string = [str(i) for i in board]

    await ctx.send("So, uh, here is board?" , view=View(board, authorized_user = ctx.author))

def setup(bot):
    bot.add_command(battleship)
