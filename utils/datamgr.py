import discord, asyncio, aiomysql, random, uuid
from typing import List, Union, NamedTuple, Dict, Optional, Any, Callable, Awaitable, Tuple
from discord.ext import commands
from random import randint
from enum import Enum
from .basemgr import *
from . import errors

class SettingType(Enum):
    select = 0

class Setting(rtData):
    def __init__(self, name: str, title: str, description: str, type: Any, default: Any):
        self.name = name
        self.title = title
        self.description = description
        self.type = type
        self.default = default

class SettingData(rtData):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

class Item(rtData):
    def __init__(self, id: str, name: str, description: str, max_count: int, icon: Union[str, int], *, tags: List[str]=[], meta: Dict={}, selling=None):
        self.id = id
        self.name = name
        self.description = description
        self.max_count = max_count
        self.icon = icon
        self.tags = tags
        self.meta = meta
        self.selling = selling

class ItemData(rtData):
    def __init__(self, id: str, count: int):
        self.id = id
        self.count = count

    def __eq__(self, item):
        return self.id == item.id

class MarketItem(rtData):
    def __init__(self, item: ItemData, *, price: int, discount: int = None):
        self.item = item
        self.price = price
        self.discount = discount

class DataDB:
    def __init__(self):
        self.items = []
        self.char_settings = []
        self.markets = {}
        self.regions = {}
        self.permissions = []
        self.exp_table = {}
        self.farm_plants = []
        self.base_exp = {}
        self.reloader = None

    def load_items(self, items: List[Item]):
        self.items = items
    
    def load_char_settings(self, settings: List[Setting]):
        self.char_settings = settings

    def load_market(self, name, market: List[MarketItem]):
        self.markets[name] = market

    def load_exp_table(self, table: Dict[int, int]):
        self.exp_table = table

    def load_base_exp(self, base_exp: Dict[str, int]):
        self.base_exp = base_exp

    def set_reloader(self, callback: Callable):
        self.reloader = callback

    def set_loader(self, callback: Callable):
        self.loader = callback

    def reload(self):
        self.reloader(self)

class ItemDBMgr(rtDBManager):
    def __init__(self, datadb: DataDB):
        self.datadb = datadb

    def fetch_item(self, itemid: str) -> Item:
        return next((item for item in self.datadb.items if item.id == itemid), None)

    def fetch_items_with(self, *, tags: Optional[list]=None, meta: Optional[dict]=None) -> List[Item]:
        foundtags = foundmeta = set(self.datadb.items)
        if tags:
            foundtags = set(filter(lambda x: set(x.tags) & set(tags), self.datadb.items))
            if not foundtags:
                return
        if meta:
            foundmeta = set(filter(lambda x: set(meta.items()) & set(x.meta.items()), self.datadb.items))
            if not foundmeta:
                return
        rst = list(foundtags & foundmeta)
        return rst

    def get_final_selling_price(self, item: ItemData, count: int=1) -> int:
        final = self.fetch_item(item.id).selling*count
        return final

class ItemMgr(rtManager):
    def __init__(self, pool: aiomysql.Pool, uid: str):
        self.pool = pool
        self.uid = uid

    async def get_items_dict(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('select * from items where id=%s', self.uid)
                itms = await cur.fetchall()
        return itms

    @classmethod
    def get_itemdata_from_dict(cls, itemdict: Dict) -> ItemData:
        return ItemData(itemdict['id'], itemdict['count'])

    @classmethod
    def get_dict_from_itemdata(cls, item: ItemData) -> Dict:
        return {
            'id': item.id,
            'count': item.count
        }

    async def get_items(self) -> List[ItemData]:
        itemdict = await self.get_items_dict()
        items = [self.get_itemdata_from_dict(x) for x in itemdict]
        return items

    async def delete_item(self, itemdata: ItemData, count: int= None) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                items = await self.get_items_dict()
                find_item = self.get_dict_from_itemdata(ItemData(itemdata.id, itemdata.count))
                delitem = next(
                    (
                        item for item in items
                        if item['id'] == find_item['id'] 
                        and item['count'] == find_item['count'] 
                    ),
                    None
                )
                if delitem is not None:
                    idx = items.index(delitem)
                    if count == None or items[idx]['count'] - count == 0:
                        await cur.execute('delete from items where uuid=%s', delitem['uuid'])
                    else:
                        await cur.execute('update items set count=count-%s where uuid=%s', (count, delitem['uuid']))
                else:
                    raise errors.NotFound

    async def give_item(self, itemdata: ItemData):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                items = await self.get_items_dict()
                giveitem = self.get_dict_from_itemdata(ItemData(itemdata.id, itemdata.count))
                sameitem = next((one for one in items if one['id'] == giveitem['id']), None)
                if sameitem:
                    await cur.execute('update items set count=count+%s where uuid=%s', (itemdata.count, sameitem['uuid']))
                else:
                    newitemuid = uuid.uuid4().hex
                    await cur.execute('insert into items (uuid, owner, itemid, count) values (%s, %s, %s, %s)', (
                        newitemuid, self.uid, itemdata.id, itemdata.count
                    ))

    async def fetch_money(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('select money from userdata where id=%s', self.uid)
                fetch = await cur.fetchone()
                money = int(fetch['money'])
        return money

    async def set_money(self, value: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('update userdata set money=%s where id=%s', (str(value), self.uid))

    async def give_money(self, value: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                money = self.fetch_money(self.uid)
                await cur.execute('update userdata set money=%s where id=%s', (str(money + value), self.uid))
