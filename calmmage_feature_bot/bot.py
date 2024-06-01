from aiogram import Dispatcher
from dotenv import load_dotenv
from calmmage_feature_bot.handler import ShowcaseHandler
from calmmage_feature_bot.app import ShowcaseApp

from bot_lib import (
    BotConfig,
    setup_dispatcher,
)
from bot_lib.demo import create_bot, run_bot
from calmapp.plugins import GptPlugin

plugins = [GptPlugin]  # MyPlugin,
app = ShowcaseApp(plugins=plugins)
bot_config = BotConfig(app=app, handlers=[ShowcaseHandler])

# set up dispatcher
dp = Dispatcher()

# handler = ShowcaseHandler()
# handlers = [handler]
setup_dispatcher(dp, bot_config)  # , extra_handlers=handlers)

load_dotenv()
bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
