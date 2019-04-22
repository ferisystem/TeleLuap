from telepot.loop import MessageLoop
from telepot import Bot
from lupa import LuaRuntime
from config import TOKEN, plugins
import time
import re

lua = LuaRuntime(unpack_returned_tuples=True)

bot = Bot(TOKEN)

patterns = []

for plg in plugins:
    script = open("plugins/{}.lua".format(plg)).read()
    lua.execute(script)
    lua_vars = lua.globals()
    if lua_vars.patterns:
        for p in lua_vars.patterns.values():
            pattern = re.compile(p)
            patterns.append((pattern, lua_vars.run))


class LuaMatches(object):
    def __init__(self, li):
        self.li = li

    def __getitem__(self, index):
        try:
            return self.li.__getitem__(index - 1)
        except IndexError:
            return


def handle(message):
    if "text" in message:
        for p, f in patterns:
            match = re.match(p, message['text'])
            if match:
                matches = list()
                re_matches = match.groups()
                if re_matches:
                    matches.extend(re_matches)
                res = f(bot, message, LuaMatches(matches))
                if isinstance(res, str):
                    bot.sendMessage(
                        message['chat']['id'],
                        res,
                        reply_to_message_id=message['message_id'])


MessageLoop(bot, handle).run_as_thread()
while 1:
    time.sleep(10)
