import discord,aiomysql
from discord.ext import commands
from . import errors

class checks:
    def __init__(self, pool: aiomysql.Pool):
        self.pool=pool

    async def money0up(self, ctx):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', ctx.author.id) != 0:
                    await cur.execute('select money from userdata where id=%s', ctx.author.id)
                    fetch = await cur.fetchone()
                    if int(fetch["money"]) >= 0:
                        return True
                    raise errors.NoMoney
                else: raise errors.NotRegistered

    async def blacklist(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', ctx.author.id) != 0:
                    await cur.execute('select blacklist from userdata where id=%s', ctx.author.id)
                    fetch = await cur.fetchone()
                    if int(fetch["blacklist"]) == 0:
                        return True
                    raise errors.blacklistuser
                else: return True

    async def master(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('select adminuser from userdata where id=%s', ctx.author.id)
                fetch = await cur.fetchone()
                if int(fetch["adminuser"]) == 1:
                    return True
                elif ctx.author.id == 467666650183761920:
                    return True
                raise errors.NotMaster
    
    async def registered(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', ctx.author.id) != 0:
                    return True
                raise errors.NotRegistered

    async def already_registered(self, ctx):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', ctx.author.id) == 0:
                    return True
                raise errors.AlreadyRegistered