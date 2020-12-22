import discord,json,asyncio,aiomysql,uuid,random
from random import randint
from discord.ext import commands 
from utils import errors,checks

def get_embed(title, description='', color=0xCCFFFF):
    embed=discord.Embed(title=title,description=description,color=color)
    return embed

class reinforce(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        self.checks = checks.checks(self.pool)

        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)
            cmds.add_check(self.checks.blacklist)

    @commands.group(name='강화', aliases=['강'], invoke_without_command=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _reinforce(self, ctx, *, weapon):
        user = ctx.author.id
        if not weapon:
            await ctx.send("알티야 강화 (이름)의 형식으로 사용해주세용")
            return
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('SELECT * FROM reinforce WHERE id = %s and name = %s',(user,weapon)) == 0:
                    await cur.execute('SELECT * FROM reinforce WHERE id = %s',user)
                    fetch = await cur.fetchall()
                    if len(fetch) >= 20:
                        await ctx.send(embed=get_embed('<a:no:698461934613168199> | 강화는 최대 20개까지 가능합니다.',"<알티야 강화 삭제 (이름)> 또는 <알티야 강화 판매 (이름)>으로 강화 수를 줄여주세요", 0xFF0000))
                        return
                    else: 
                        await cur.execute('INSERT INTO reinforce VALUES (%s,%s,%s,%s)',(uuid.uuid4().hex,weapon,user,0))
                
                await cur.execute('SELECT level FROM reinforce WHERE id = %s and name = %s',(user,weapon))
                fetch = await cur.fetchone()
                level=fetch["level"]

                #############################################
                
                if level >= 100:
                    msg = await ctx.send(embed=get_embed(":hammer: | 특수 강화","100렙을 넘으셔서 특수강화 도전을 하실수 있습니다.\n성공 : 50% (5~20 레벨 랜덤 오름)\n실패 : 50% (실패시 80레벨)\n도전 하시겠습니까?"))
                    emjs=['<a:yes:698461934198063104>','<a:no:698461934613168199>']
                    await msg.add_reaction(emjs[0])
                    await msg.add_reaction(emjs[1])
                    def check(reaction, user):
                        return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
                        return
                    else:
                        e = str(reaction.emoji)
                        if e == '<a:yes:698461934198063104>':
                            rand = randint(0,1)
                            if rand == 1:
                                n = randint(5,20)
                                await cur.execute('UPDATE reinforce SET level = %s WHERE id = %s and name = %s',(level+n, ctx.author.id, weapon))
                                await ctx.send(embed=get_embed(f"<a:yes:698461934198063104> | {weapon} (이)가 **{n}레벨** 성장했습니다.",f"현재 레벨 : **{level+n}**"))
                                return
                            else:
                                await cur.execute('UPDATE reinforce SET level = 80 WHERE id = %s and name = %s',(ctx.author.id, weapon))
                                await ctx.send(embed=get_embed(f"<a:no:698461934613168199> | {weapon} (이)가 파괴되었습니다.","",0xff0000))
                                return
                        elif e == '<a:no:698461934613168199>':
                            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                            return

                #############################################

                else:
                    rand = randint(0,100) - level
                    if rand > 0:
                        n = randint(2,10)
                        await cur.execute('UPDATE reinforce SET level = %s WHERE id = %s and name = %s',(level+n, ctx.author.id, weapon))
                        await ctx.send(f"**성공!** {weapon} (이)가 **{100-level}%**의 확률로 **{n}레벨** 성장했습니다\n현재 레벨 : **{level+n}**")
                    else: 
                        n=randint(1,5)
                        await cur.execute('UPDATE reinforce SET level = %s WHERE id = %s and name = %s',(level-n, ctx.author.id, weapon))
                        await ctx.send(f"**실패..** {weapon}이가 **{level}%**의 확률로 **{n}레벨** 하강ㅠㅠ\n현재 레벨 : **{level-n}**")

    @_reinforce.command(name='목록', aliases=['물품','리스트'])
    async def _rf_list(self, ctx):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT * FROM reinforce WHERE id = %s',ctx.author.id)
                fetch = await cur.fetchall()
        lis = []
        for s in fetch:
            lis.append(f"**Lv {s['level']}**  {s['name']}")
        await ctx.send(embed=get_embed(f":wrench: **{ctx.author} 님의 강화 목록**","\n".join(lis)))

    @_reinforce.command(name='삭제')
    async def _rf_erase(self, ctx, *, arg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('SELECT * FROM reinforce WHERE id = %s and name = %s',(ctx.author.id,arg)) == 0:
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 찾을수 없는 물품입니다.","",0xff0000))
                    return

                await cur.execute('SELECT level FROM reinforce WHERE id = %s and name = %s',(ctx.author.id,arg))
                fetch = await cur.fetchone()
                level=fetch["level"]

                msg  = await ctx.send(embed=get_embed("📄 | 강화 삭제",f"**Lv.{level} {arg}**\n\n정말 삭제 하시겠습니까?"))
                emjs=['<a:yes:698461934198063104>','<a:no:698461934613168199>']
                await msg.add_reaction(emjs[0])
                await msg.add_reaction(emjs[1])
                def check(reaction, user):
                    return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
                try:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await asyncio.gather(
                        msg.delete(),
                        ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                        )
                    return
                else:
                    e = str(reaction.emoji)
                    if e == '<a:yes:698461934198063104>':
                        await cur.execute('DELETE from reinforce WHERE id = %s and name = %s',(ctx.author.id,arg))
                        await ctx.send(embed=get_embed("<a:yes:698461934198063104> | 삭제 완료!"))
                        return
                    elif e == '<a:no:698461934613168199>':
                        await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                        return

    @_reinforce.command(name='판매')
    async def _rf_sell(self, ctx, *, arg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('SELECT * FROM reinforce WHERE id = %s and name = %s',(ctx.author.id, arg)) == 0:
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 찾을 수 없는 물품입니다.","",0xff0000))
                    return

                await cur.execute('SELECT level FROM reinforce WHERE id = %s and name = %s',(ctx.author.id, arg))
                fetch = await cur.fetchone()
                level=fetch["level"]

                if level < 60:
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 60레벨 이상의 물품만 판매하실수 있습니다.","<알티야 강화 삭제> 명령어로 삭제가 가능합니다.",0xff0000))
                    return

                n = 2 ** (level - 45)

                msg  = await ctx.send(embed=get_embed("📄 | 강화 판매",f"**Lv.{level} {arg}**\n\n의 가치는 {n}입니다.\n정말 판매 하시겠습니까?"))
                emjs=['<a:yes:698461934198063104>','<a:no:698461934613168199>']
                for a in emjs: await msg.add_reaction(a)
                def check(reaction, user):
                    return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
                try:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await asyncio.gather(
                        msg.delete(),
                        ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                        )
                    return
                else:
                    e = str(reaction.emoji)
                    if e == '<a:yes:698461934198063104>':
                        await cur.execute('DELETE from reinforce WHERE id = %s and name = %s',(ctx.author.id,arg))

                        await cur.execute('SELECT money FROM userdata WHERE id = %s', ctx.author.id)
                        fetch = await cur.fetchone()
                        money = int(fetch['money'])
                        await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+n),ctx.author.id))

                        await ctx.send(embed=get_embed("<a:yes:698461934198063104> | 판매 완료!",f'{n}원이 지급되었습니다.'))
                        return
                    elif e == '<a:no:698461934613168199>':
                        await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                        return

    @_reinforce.group(name='순위', invoke_without_command=True)
    async def _rf_rank(self, ctx):
        await ctx.send(embed=get_embed("<a:no:698461934613168199> | 올바르지 않은 명령어입니다!","알티야 강화 순위 서버/전체로 사용해주세요",0xff0000))

    @_rf_rank.command(name='서버')
    async def _rf_list_server(self, ctx):
        lis = []
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT * FROM reinforce')
                fetch = await cur.fetchall()
                for r in fetch:
                    try: user = ctx.guild.get_member(int(r["id"])).name
                    except: pass
                    else: lis.append([user, r["name"], r["level"]])
        lis.sort(key=lambda x: x[2], reverse=True)
        alis = []
        a=0
        for r in lis:
            if a ==0: medal = '<:LeaderboardTrophy01:716106586333904986>'
            elif a==1: medal = '<:silverthropy:736215959823712306>'
            elif a==2: medal = '<:bronzethropy:736215949614645269>'
            else: medal = '🏅'
            alis.append(f"{medal} | **{r[0]}**\n> **Lv{r[2]}** {r[1]}\n\n")
            a+=1
            if a>=6: break
        await ctx.send(embed=get_embed(":bar_chart: | 서버 강화 순위","".join(alis)))

    @_rf_rank.command(name='전체')
    async def _rf_list_all(self, ctx):
        lis = []
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT * FROM reinforce')
                fetch = await cur.fetchall()
                for r in fetch:
                    try: user = self.client.get_user(int(r["id"])).name
                    except: user = int(r["id"])
                    else:
                        lis.append([user, r["name"], r["level"]])
        lis.sort(key=lambda x: x[2], reverse=True)
        alis = []
        a=0
        for r in lis:
            if a ==0: medal = '<:LeaderboardTrophy01:716106586333904986>'
            elif a==1: medal = '<:silverthropy:736215959823712306>'
            elif a==2: medal = '<:bronzethropy:736215949614645269>'
            else: medal = '🏅'
            alis.append(f"{medal} | **{r[0]}**\n**Lv{r[2]}** {r[1]}\n\n")
            a+=1
            if a>=6: break
        await ctx.send(embed=get_embed(":bar_chart: | 서버 강화 순위","".join(alis)))

def setup(client):
    client.add_cog(reinforce(client))