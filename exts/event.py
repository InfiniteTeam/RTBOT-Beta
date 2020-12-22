import discord,traceback,sys
from discord.ext import commands, tasks
from utils import errors, permutil
from itertools import cycle

def get_embed(title, description='', color=0xccffff): 
    return discord.Embed(title=title,description=description,color=color)

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bg_change_playing.start()
        self.gamecycle = cycle([f"알티봇 V4.0.0", "'알티야 도움'로 봇명령어 알아보기", f"{len(self.client.guilds)} Servers│{len(self.client.users)} Users"])

    @tasks.loop(seconds=15)
    async def bg_change_playing(self):
        try:
            await self.client.change_presence(activity=discord.Game(next(self.gamecycle)))
        except:
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.client.get_channel(735563383277092874).send(f"<a:ok:689877466705297444>추가됨\n{guild.name} **{len(guild.members)}**\n현재 서버수 : {len(self.client.guilds)}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.client.get_channel(735563383277092874).send(f"<a:no:689877428142604390>제거됨\n{guild.name}\n현재 서버수 : {len(self.client.guilds)}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("==================\nRTBOT ONLINE\n==================")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        excinfo = sys.exc_info()
        errstr = f'{"".join(traceback.format_tb(excinfo[2]))}{excinfo[0].__name__}: {excinfo[1]}'
        await self.client.get_channel(728788620000886854).send(embed=get_embed("error",errstr))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        allerrs = (type(error), type(error.__cause__))

        if commands.errors.MissingRequiredArgument in allerrs:
            return

        elif isinstance(error, errors.playinggame):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 이미 다른 게임이 진행중입니다.", "",0xff0000))
            return

        elif isinstance(error, errors.blacklistuser):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 블랙리스트에 오른 상태입니다!","블랙리스트 명단에 추가되어 봇을 사용하실수 없습니다.",0xFF0000))
            return

        elif isinstance(error, errors.NotMaster):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 봇에 엑세스할 권한이 부족합니다!","필요한 권한 : `봇 어드민`",0xFF0000))
            return

        elif isinstance(error, errors.NotRegistered):
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 가입 되어 있지 않습니다!',"<알티야 가입> 으로 가입해주세요", 0xFF0000))
            return

        elif isinstance(error, errors.NoMoney):
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 돈이 부족합니다!','',0xff0000))
            return

        elif isinstance(error, errors.AlreadyRegistered):
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 이미 가입 되어 있습니다!',"", 0xFF0000))
            return

        elif isinstance(error, errors.morethan1):
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 1원 이상의 정수값을 입력해주세요!',"", 0xFF0000))
            return

        ################################################################################################################################

        elif isinstance(error, discord.NotFound):
            return

        elif isinstance(error, commands.errors.CommandNotFound):
            return

        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 명령어 양식을 지켜주세요!","입력한 명령어가 올바른지 확인해주세요",0xFF0000))
            return

        elif isinstance(error, commands.MissingPermissions):
            perms = [permutil.format_perm_by_name(perm) for perm in error.missing_perms]
            embed = get_embed("<a:no:698461934613168199> | 멤버 권한 부족!",
                f"{self.ctx.author.mention}, 이 명령어를 사용하려면 다음과 같은 길드 권한이 필요합니다!\n> **`"
                + "`, `".join(perms)
                + "`**",
            )
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 멤버 권한 부족!',f'{ctx.author.mention}, 이 명령어를 사용하려면 다음과 같은 길드 권한이 필요합니다!\n`'+ '`, `'.join(perms) + '`',0xFF0000))
            return

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 서버내 사용 가능 명령어입니다!","서버에서만 사용해주세요",0xFF0000))
            return

        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | DM 전용 명령어입니다!","디엠에서만 사용해주세요",0xFF0000))
            return

        elif errors.ParamsNotExist in allerrs:
            await ctx.send(embed=get_embed(f'<a:no:698461934613168199> | 존재하지 않는 명령 옵션입니다: {", ".join(str(error.__cause__.param))}',f'`알티야 도움` 명령으로 전체 명령어를 확인할 수 있어요.',0xFF0000))
            return
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if int(error.retry_after) > 1:
                await ctx.send(embed=get_embed("<a:no:698461934613168199> | 명령어를 조금만 천천히 써주세요!",'{:.2f}초만 기다려주세요!'.format(error.retry_after),0xFF0000))
            return

        elif isinstance(error, commands.errors.MissingPermissions):
            return

        elif errors.ParamsNotExist in allerrs:
                embed = discord.Embed(title=f'❓ 존재하지 않는 명령 옵션입니다: {", ".join(str(error.__cause__.param))}', description=f'`알티야 도움` 명령으로 전체 명령어를 확인할 수 있어요.', color=self.color['error'])
                await ctx.send(embed=embed)
                return

        elif isinstance(error, errors.SentByBotUser):
            return

        elif isinstance(error.__cause__, discord.HTTPException):
            if error.__cause__.code in [50013, 50001]:
                try: 
                    missing_perms = []
                    fmtperms = [permutil.format_perm_by_name(perm) for perm in missing_perms]
                    if missing_perms:
                        embed = get_embed(
                            "⛔ 봇 권한 부족!",
                            "이 명령어를 사용하는 데 필요한 봇의 권한이 부족합니다!\n`"
                            + "`, `".join(fmtperms)
                            + "`",
                        )
                    else:
                        embed = get_embed(
                            "⛔ 봇 권한 부족!",
                            "이 명령어를 사용하는 데 필요한 봇의 권한이 부족합니다!\n부족한 권한이 무엇인지 감지하는 데 실패했습니다.",
                        )
                    await ctx.send(embed=embed)
                except discord.Forbidden:
                    embed = get_embed("⛔ 메시지를 보낼 수 없습니다!",
                        f"""\
                            방금 [명령어]({ctx.message.jump_url})를 입력하신 채널에서 알티봇에 `메시지 전송하기` 또는 `링크 전송` 권한이 없어 메시지를 보낼 수 없습니다. 서버 관리자에게 문의해주세요.
                            **(`{ctx.guild}` 서버의 `{ctx.channel}` 채널)**
                        """,
                    )
                    await ctx.author.send(embed=embed)
                return

            elif error.__cause__.code == 50035:
                await ctx.send(embed=get_embed('<a:no:698461934613168199> | 메시지 전송 실패','보내려고 하는 메시지가 너무 길어 전송에 실패했습니다.',0xff0000))
                return

            elif error.__cause__.code == 50005:
                await ctx.send(embed=get_embed('<a:no:698461934613168199> | 메시지 수정 실패','타인의 메세지는 수정불가합니다.',0xff0000))
                return

            elif error.__cause__.code == 50003:
                await ctx.send(embed=get_embed('<a:no:698461934613168199> | Cannot execute action on a DM channel','DM에서 할수 없는 명령어 입니다.',0xff0000))
                return

            elif error.__cause__.code == 50007:
                embed = get_embed('<a:no:698461934613168199> | 메시지 전송 실패', 'DM(개인 메시지)으로 메시지를 전송하려 했으나 실패했습니다.\n혹시 DM이 비활성화 되어 있지 않은지 확인해주세요!',0xff0000)
                await ctx.send(ctx.author.mention, embed=embed)
                return
            
            elif error.__cause__.code == 10008:
                return

            else:
                embed = get_embed('<a:no:698461934613168199> | 알 수 없는 에러', '오류 코드: ' + str(error.__cause__.code) + "\n[알티봇 서포트 서버](https://discord.gg/hTZxtbC)에서 도움을 드립니다.",0xff0000)
                await ctx.send(embed=embed)
                return

        if ctx.author.id == 467666650183761920:
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | **ERROR**!',f'무언가 오류가 발생했습니다!\n```python\n{traceback.format_exception(type(error), error, error.__traceback__)}```tlqkf',0xFF0000))

        else:
            await ctx.send(embed=get_embed('<a:no:698461934613168199> | 알 수 없는 에러발생!','[알티봇 서포트 서버](https://discord.gg/hTZxtbC)에서 도움을 드립니다.',0xff0000))
            await self.client.get_channel(728788620000886854).send(embed=get_embed('<a:no:698461934613168199> | **ERROR**!',f'Id : {ctx.author.id}\nContent : {ctx.message.content}```python\n{traceback.format_exception(type(error), error, error.__traceback__)}```ㅄ',0xFF0000))

def setup(client):
    client.add_cog(events(client))