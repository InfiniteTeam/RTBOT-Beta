import discord, os, asyncio, aiomysql, json
from discord.ext import commands

with open("./config/config.json", "r", encoding='UTF8') as db_json: config = json.load(db_json)

loop = asyncio.get_event_loop()

async def connect_db():
    pool = await aiomysql.create_pool(
        host=config["db"]["host"],
        user=config["db"]["user"],
        password=config["db"]["password"],
        db=config["db"]["db"],
        charset=config["db"]["charset"],
        autocommit=True
    )
    return pool
    
pool = loop.run_until_complete(connect_db())

client = commands.AutoShardedBot(command_prefix=config["command_prefix"],intents=discord.Intents.all())
client.pool = pool

for ext in filter(lambda x: x.endswith('.py') and not x.startswith('_'), os.listdir('./exts')):
    client.load_extension('exts.' + os.path.splitext(ext)[0])

client.run(config["token"])