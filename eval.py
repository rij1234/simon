from discord.ext import commands
import discord
import ast
from prettytable import PrettyTable

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


@commands.command(aliases=["eval","e"], hidden=True)
@commands.is_owner()
async def evaluate(ctx,*,cmd):
    fn_name = "_eval_expr"
#    return await ctx.send(cmd)
    cmd.replace("```py", "")
    if cmd.endswith('```'):
        cmd = cmd[:-3]
    if cmd.startswith('```py'):
        cmd = cmd[5:]
    if cmd.startswith('```'):
        cmd = cmd[3:]

    # add a layer of indentation
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
    try:
        await ctx.send(f"```{result}```")
    except:
        return

@commands.command(hidden=True)
@commands.is_owner()
async def sql(ctx, *, cmd):
    db = ctx.bot.db
    cur = await db.execute(cmd)
    data = await cur.fetchall()
    table = PrettyTable([col_info[0] for col_info in cur.description])
    for i in data:
        table.add_row(i)
    table = str(table).split("\n")
    paginator_table = commands.Paginator()
    for i in table:
        paginator_table.add_line(i)
    for pages in paginator_table.pages:
        await ctx.send(pages)

@commands.command()
@commands.is_owner()
async def toggletraceback(ctx):
    ctx.bot.toggle_traceback()
    await ctx.message.add_reaction("\N{THUMBS UP SIGN}")

def setup(bot):
    bot.add_command(evaluate)
    bot.add_command(sql)
    bot.add_command(toggletraceback)
