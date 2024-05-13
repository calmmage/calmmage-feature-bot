import asyncio
from dotenv import load_dotenv

load_dotenv(".env")
from calmmage_feature_bot.bot import bot, dp


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
