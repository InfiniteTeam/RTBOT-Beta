import discord,json,asyncio,aiomysql,traceback
from discord.ext import commands 
from utils import errors,checks

with open("./data/noticechannel.json", "r", encoding='UTF8') as db_json: noticedb = json.load(db_json)

def get_embed(title, description='', color=0xCCFFFF):
    embed=discord.Embed(title=title,description=description,color=color)
    return embed

class admincmds(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        self.checks = checks.checks(self.pool)

        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)
            cmds.add_check(self.checks.master)

    @commands.command(name='eval')
    async def _eval(self, ctx, *, arg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try: await ctx.send(embed=get_embed('관리자 기능 - Eval',f"📤 OUTPUT```{eval(arg)}```"))
                except Exception as a: await ctx.send(embed=get_embed('관리자 기능 - Eval',f"📤 EXCEPT```{traceback.format_exc()}```",0xFF0000))

    @commands.command(name='hawait')
    async def _await(self, ctx, *, arg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try: await eval(arg)
                except Exception as a: await ctx.send(embed=get_embed('관리자 기능 - hAwait Eval',f"📤 EXCEPT```{traceback.format_exc()}```",0xFF0000))

    @commands.command(name='await')
    async def _awa_it(self, ctx, *, arg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try: res = await eval(arg) 
                except Exception as a: await ctx.send(embed=get_embed('관리자 기능 - Await Eval',f"📤 EXCEPT```{traceback.format_exc()}```",0xFF0000))
                else: await ctx.send(embed=get_embed('관리자 기능 - Eval',f"📤 OUTPUT```{res}```"))

    @commands.command(name='강화설정')
    async def reinforce_set(self, ctx, uid: int, name: str, level: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('UPDATE reinforce set level = %s WHERE id = %s and name = %s',(level,uid,name))
    
    @commands.command(name='돈설정')
    async def _money_set(self,ctx,uid,n:int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(n), uid))
        await ctx.send(f"SETTED money\nuid: {uid}\nn: {n}")

    @commands.command(name='은행설정')
    async def _bank_set(self, ctx, uid, n:int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('UPDATE userdata set bank=%s WHERE id = %s', (str(n), uid))
        await ctx.send(f"SETTED bank\nuid: {uid}\nn: {n}")

    @commands.command(name='강제가입')
    async def _force_register(self, ctx: commands.Context, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', uid) != 0:
                    await ctx.send("Already Registered")
                    return
                await cur.execute('INSERT INTO userdata VALUES(%s, "5000", 0, 0, 0)', uid)
                await ctx.send(f"Setted\nuid: {uid}")

    @commands.command(name='유저등록확인')
    async def _check_user_existing(self, ctx: commands.Context, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', uid) != 0:
                    await cur.execute('select * from userdata where id=%s', uid)
                    fetch = await cur.fetchall()
                    await ctx.send(f"Registered USER : {uid}\n{fetch}")
                    return
                await ctx.send("Not registered")

    @commands.command(name='어드민추가')
    async def _add_admin(self, ctx: commands.Context, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', uid) == 0:
                    await cur.execute('INSERT INTO userdata VALUES(%s, "5000", 0, 1, 0)', uid)
                    await ctx.send("Done. + force registered")
                    return
                await cur.execute('UPDATE userdata set adminuser = 1 WHERE id = %s', uid)
                await ctx.send("Done.")

    @commands.command(name="블랙추가")
    async def _up_black(self, ctx, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', uid) == 0:
                    await cur.execute('INSERT INTO userdata VALUES(%s, "5000", 0, 0, 1)', uid)
                    await ctx.send("Done. + force registered")
                    return
                await cur.execute('UPDATE userdata set blacklist = 1 WHERE id = %s', uid)
                await ctx.send("Done.")

    @commands.command(name="블랙제거")
    async def _down_black(self, ctx, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', uid) == 0:
                    await ctx.send("Not Registered")
                    return
                await cur.execute('UPDATE userdata set blacklist = 0 WHERE id = %s', uid)

    @commands.command(name='공지보내')
    async def _notice_send(self, ctx, *, arg):
        if ctx.author.id != 467666650183761920: raise errors.NotMaster
        lis =[]
        for s in self.client.guilds:
            sendedserver = s.name
            schannel = ''
            if str(s.id) in noticedb.keys():
                schannel=self.client.get_channel(noticedb[str(s.id)])
            else:
                for channel in s.text_channels:
                    if channel.permissions_for(s.me).send_messages:
                        freechannel = channel
                        if '공지' in channel.name and '봇' in channel.name:
                            schannel = channel
                            break
                        elif 'noti' in channel.name.lower() and 'bot' in channel.name.lower():
                            schannel = channel
                            break
                        elif '공지' in channel.name:
                            schannel = channel
                            break
                        elif 'noti' in channel.name.lower():
                            schannel = channel
                            break
                        elif '봇' in channel.name:
                            schannel = channel
                            break
                        elif 'bot' in channel.name.lower():
                            schannel = channel
                            break
                if schannel == '':
                    schannel = freechannel
            try: 
                await schannel.send(embed=get_embed(":warning: | 알티봇 공지",arg+"\n\n[인피니트 서포트 서버](https://discord.gg/7aFczQk)\n[알티봇 서포트 서버](https://discord.gg/hTZxtbC)\n[알티봇 초대하기](https://discordapp.com/api/oauth2/authorize?client_id=661477460390707201&permissions=8&scope=bot)"))
                lis.append('<a:yes:698461934198063104> '+sendedserver)
            except: 
                lis.append('<a:no:698461934613168199> '+sendedserver)
        await ctx.send(embed=get_embed("공지 전송 완료","\n".join(lis)))

def setup(client):
    client.add_cog(admincmds(client))