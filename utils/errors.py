from discord.ext import commands
from typing import List, Tuple, Union

class NotRegistered(commands.CheckFailure):
    pass

class NotMaster(commands.CheckFailure):
    pass

class AlreadyRegistered(commands.CheckFailure):
    pass

class NoMoney(commands.CheckFailure):
    pass

class morethan1(commands.CheckFailure):
    pass

class GlobaldataAlreadyAdded(Exception):
    pass

class SentByBotUser(commands.CheckFailure):
    pass

class LockedExtensionUnloading(Exception):
    pass

class blacklistuser(Exception):
    pass

class playinggame(Exception):
    pass

class NotFound(Exception):
    pass

class MissingRequiredArgument(commands.CheckFailure):
    def __init__(self, param, paramdesc):
        self.param = param
        self.paramdesc = paramdesc
        super().__init__('명령어 파라미터 "{}"({})이 필요합니다'.format(param.name, paramdesc))

class ParamsNotExist(Exception):
    def __init__(self, param):
        self.param = param
        super().__init__('존재하지 않는 옵션값입니다: {}'.format(param))

class NotGuildChannel(commands.CheckFailure):
    pass