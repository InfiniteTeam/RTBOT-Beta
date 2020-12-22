import discord, requests, datetime, bs4, urllib, asyncio
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

def get_embed(title, description='', color=0xCCFFFF): 
    return discord.Embed(title=title,description=description,color=color)

class supportserver(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greetings = member.guild.get_channel(680707161290047489)
        await greetings.send(embed=discord.Embed(title='👋 안녕하세요!', description=f'{member.mention}님, 반갑습니다! 알티봇 서포트 서버에 어서오세요!', color=0xccffff))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        greetings = member.guild.get_channel(680707161290047489)
        await greetings.send(embed=discord.Embed(title='👋 안녕히가세요-', description=f'{member.name}님이 나갔습니다.', color=0xccffff))

def setup(client):
    client.add_cog(supportserver(client))