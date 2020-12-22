import discord,json,asyncio,aiomysql, typing, random
from discord.ext import commands 
from random import randint
from utils import errors,checks

with open("./data/noticechannel.json", "r", encoding='UTF8') as db_json: noticedb = json.load(db_json)

def get_embed(title, description='', color=0xCCFFFF):
    embed=discord.Embed(title=title,description=description,color=color)
    return embed

class minigame(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        self.checks = checks.checks(self.pool)   

        self.gaming_list = []

        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)
            cmds.add_check(self.checks.blacklist)

    async def start_game(self, uid: int):
        if uid in self.gaming_list: raise errors.playinggame

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT money FROM userdata WHERE id = %s', uid)
                fetch = await cur.fetchone()
                self.gaming_list.append(uid)
                return int(fetch["money"])

    @commands.group(name='가위바위보', invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def rsp(self, ctx, n: typing.Union[str, None] = None):
        money = await self.start_game(ctx.author.id)
        
        emjs=['✋','✌️','✊']
        botsay=randint(0,2)
        usrsay=0

        if not n:
            embed=get_embed("✊ | 묵,찌,빠중 하나를 골라주세요!")
            embed.set_footer(text="0,x,X 중하나를 입력하면 취소됩니다.")
            await ctx.send(embed=embed)

            def check(author):
                def inner_check(message): 
                    if message.author != author: return False
                    else: return True
                return inner_check
            try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
            except asyncio.TimeoutError: 
                self.gaming_list.remove(ctx.author.id)
                await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                return
            else: 
                n = msg.content
                if n in ["0","X","x"]:
                    self.gaming_list.remove(ctx.author.id)
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                    return

        givemoney = randint(500,5000)
        status = "DRAW"

        if n in ["빠","보자기","보"]: 
            usrsay = 0
            if botsay == 1: status = "WIN"
            elif botsay == 2: status = "LOSE"

        elif n in ["찌","가위"]: 
            usrsay = 1
            if botsay == 2: status = "WIN"
            elif botsay == 0: status = "LOSE"

        elif n in ["묵","바위"]: 
            usrsay = 2
            if botsay == 0: status = "WIN"
            elif botsay == 1: status = "LOSE"

        else:
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 알맞지 않은 명령어 양식입니다.","가위바위보 빠, 가위바위보 묵, 가위바위보 찌 셋중 하나를 골라서 해주세요"))
            self.gaming_list.remove(ctx.author.id)
            return

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT money FROM userdata WHERE id = %s', ctx.author.id)
                fetch = await cur.fetchone()
                money = fetch["money"]
                if status == "DRAW":
                    await ctx.send(f"비겼습니다! **{int(givemoney//2)}원**을 가져갈께요!\n당신의 선택 : {emjs[usrsay]}\n봇의 선택 : {emjs[botsay]}")
                    if money-int(givemoney//2) < 0: 
                        await cur.execute('UPDATE userdata set money="0" WHERE id = %s', ctx.author.id)
                    else:
                        await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money-int(givemoney//2)),ctx.author.id))
                elif status == "WIN":
                    await ctx.send(f"이겼습니다! {givemoney}원을 드릴께요! 당신의 선택 : {emjs[usrsay]}\n봇의 선택 : {emjs[botsay]}")
                    await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+givemoney),ctx.author.id))
                elif status == "LOSE":
                    await ctx.send(f"졌습니다! {givemoney}원을 가져갈께요! 당신의 선택 : {emjs[usrsay]}\n봇의 선택 : {emjs[botsay]}")
                    if money-givemoney < 0: 
                        await cur.execute('UPDATE userdata set money="0" WHERE id = %s', ctx.author.id)
                    else:
                        await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money-givemoney),ctx.author.id))
        self.gaming_list.remove(ctx.author.id)
                    
                    
    
    @commands.command(name="숫자맞추기", aliases=['숫맞','업다운','업다운게임'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def updown(self, ctx, n: typing.Union[str, int, None] = None):

        money = await self.start_game(ctx.author.id)

        if not n:
            await ctx.send(embed=get_embed("💵 | 거실금액을 입력해주세요"))

            def check(author):
                def inner_check(message): 
                    if message.author != author: return False
                    else: return True
                return inner_check
            try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
            except asyncio.TimeoutError: 
                self.gaming_list.remove(ctx.author.id)
                await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                return
            else: 
                n = msg.content
                if n in ["0","X","x"]:
                    self.gaming_list.remove(ctx.author.id)
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                    return

        try: int(n)
        except:
            if n in ["올인","전부","전체","최대"]: n=money
            else: 
                self.gaming_list.remove(ctx.author.id)
                raise errors.morethan1
        else: n = int(n)

        if n <= 0: 
            self.gaming_list.remove(ctx.author.id)
            raise errors.morethan1

        if n > money: 
            self.gaming_list.remove(ctx.author.id)
            raise errors.NoMoney
        
        embed=get_embed("⚖️ | 숫자맞추기 난이도를 정해주세요","실패시 걸은돈은 삭제됩니다.")
        embed.add_field(name="😀 | 쉬움",value="1~10까지의 수중 뽑습니다.\n보상 : 걸은돈의 1 ~ 2배")
        embed.add_field(name="😠 | 보통",value="1~20까지의 수중 뽑습니다.\n보상 : 걸은돈의 2 ~ 4배")
        embed.add_field(name="🤬 | 어려움",value="1~30까지의 수중 뽑습니다.\n보상 : 걸은돈의 3 ~ 6배")
        embed.set_footer(text="❌를 눌러 취소")
        msg = await ctx.send(embed=embed)

        number = 0
        lev = 0
        emjs=['😀','😠','🤬','❌']
        for em in emjs: await msg.add_reaction(em)

        def check(reaction, user):
            return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try: reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
            self.gaming_list.remove(ctx.author.id)
            return
        else:
            e = str(reaction.emoji)
            if e == '😀':
                number = randint(1,10)
                lev = 1
            elif e == '😠':
                number = randint(1,20)
                lev = 2
            elif e == '🤬':
                number = randint(1,30)
                lev = 3
            elif e == '❌':
                self.gaming_list.remove(ctx.author.id)
                await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                return

        await ctx.send(embed=get_embed('입력해주세요'))

        def check(author):
            def inner_check(message): 
                if message.author != author: return False
                try: int(message.content) 
                except ValueError: return False
                else: return True
            return inner_check
        
        try: 
            msg = await self.client.wait_for('message',check=check(ctx.author),timeout=30)
        except asyncio.TimeoutError: 
            await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
            self.gaming_list.remove(ctx.author.id)
            return

        number = abs(int(msg.content)-number)
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('SELECT money FROM userdata WHERE id = %s', ctx.author.id)
                fetch = await cur.fetchone()
                money = fetch["money"]
                await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money-n),ctx.author.id))
                if number == 0:
                    lev = lev * 2
                    await ctx.send(f'정확합니다!! {n*lev} 원 지급! \n**({lev}배)**')
                    await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+n*lev),ctx.author.id))
                elif number == 1:
                    lev = lev * 1.5
                    await ctx.send(f'1차이! {int(n*lev)} 원 지급! \n**({lev}배)**')
                    await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+int(n*lev)),ctx.author.id))
                elif number == 2:
                    await ctx.send(f'2차이, {n*lev} 원 지급! \n**({lev}배)**')
                    await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+n*lev),ctx.author.id))
                else:
                    await ctx.send(f'맞추지 못했습니다...')
        self.gaming_list.remove(ctx.author.id)

    @commands.group(name="슬롯")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def slot(self, ctx, n: typing.Union[str, int, None] = None):

        money = await self.start_game(ctx.author.id)

        if not n:
            embed=get_embed("💵 | 거실금액을 입력해주세요")
            embed.set_footer(text="0,x,X 중하나를 입력하면 취소됩니다.")
            await ctx.send(embed=embed)
            def check(author):
                def inner_check(message): 
                    if message.author != author: return False
                    else: return True
                return inner_check
            try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
            except asyncio.TimeoutError: 
                self.gaming_list.remove(ctx.author.id)
                await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                return
            else: 
                n = msg.content
                if n in ["0","X","x"]:
                    self.gaming_list.remove(ctx.author.id)
                    await ctx.send(embed=get_embed("<a:no:698461934613168199> | 취소 되었습니다.","",0xff0000))
                    return

        try: int(n)
        except:
            if n in ["올인","전부","전체","최대"]: n=money//200
            else: 
                self.gaming_list.remove(ctx.author.id)
                raise errors.morethan1
        else: n = int(n)

        if n < 0: 
            self.gaming_list.remove(ctx.author.id)
            raise errors.morethan1

        if n == 0:
            self.gaming_list.remove(ctx.author.id)
            raise errors.NoMoney

        if n > money: 
            self.gaming_list.remove(ctx.author.id)
            raise errors.NoMoney

        if money < 2000:
            self.gaming_list.remove(ctx.author.id)
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 최소 2000원의 자산이 있어야 가능합니다.", f"현재 금액 : {money}",0xff0000))
            return

        if n > money//200:
            self.gaming_list.remove(ctx.author.id)
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 현재 금액의 200분의 1 이상 사용불가합니다.", f"최대사용금액 : {money//200}",0xff0000))
            return
        allslot = ['🔔','⭐','🍒','🍈','❌','💩']
        slotbae = [10,6,2,0,-1,-2]
        msg=await ctx.send(embed=get_embed("🎰 | 슬롯",f"🔔 **10** \n⭐ **6** \n🍒 **2** \n🍈 **0** \n❌ **-1** \n💩 **-2** \n\n금액 : {n}\n참여 하시겠습니까?"))
        emjs=['<a:yes:698461934198063104>','<a:no:698461934613168199>']
        for em in emjs: await msg.add_reaction(em)
        def check(reaction, user):
            return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=20)
        except asyncio.TimeoutError:
            await asyncio.gather(
                msg.delete(),
                ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                )
            self.gaming_list.remove(ctx.author.id)
        else:
            e = str(reaction.emoji)
            if e == '<a:yes:698461934198063104>':
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cur:
                        msg1=await ctx.send("❓ ❓ ❓")
                        await asyncio.sleep(3)
                        slot=random.choices(list(range(0,6)), weights = [20,15,20,5,20,20], k = 3)
                        await msg1.edit(content=f"❓ ❓ {allslot[slot[0]]}")
                        await asyncio.sleep(2)
                        await msg1.edit(content=f"❓ {allslot[slot[1]]} {allslot[slot[0]]}")
                        await asyncio.sleep(2)
                        await msg1.edit(content=f"{allslot[slot[2]]} {allslot[slot[1]]} {allslot[slot[0]]}")
                        bae = 1
                        for a in slot: bae = bae * slotbae[a]
                        if n*bae > 0:
                            await ctx.send(f"{n*bae}원 획득!\n(**총 배수 : {bae}**)")
                        elif n*bae == 0:
                            await ctx.send(f"(**총 배수 : 0**)")
                        elif n*bae< 0:
                            await ctx.send(f"{n*bae*-1}원 을 잃었습니다!\n(**총 배수 : {bae}**)")

                        await cur.execute('SELECT money FROM userdata WHERE id = %s', ctx.author.id)
                        fetch = await cur.fetchone()
                        money = fetch["money"]
                        
                        await cur.execute('UPDATE userdata set money=%s WHERE id = %s', (str(money+n*bae),ctx.author.id))
                        self.gaming_list.remove(ctx.author.id)
                        return
            elif e == '<a:no:698461934613168199>':
                await asyncio.gather(
                    msg.delete(),
                    ctx.send(embed=get_embed('<a:no:698461934613168199> | 취소 되었습니다!',"", 0xFF0000))
                )
                self.gaming_list.remove(ctx.author.id)
                return
        self.gaming_list.remove(ctx.author.id)
        return

def setup(client):
    client.add_cog(minigame(client))