import discord
from discord.ext import commands
import asyncpg
import asyncio
import re
import os
import dotenv
from config import extensions, db_config, db_engine
import datetime


class MyBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_cache = []

    async def on_ready(self):
        print(
            f"{str(self.user)} started successfully. latency is {self.latency * 1000}ms"
        )
        self.launch_time = datetime.datetime.now()

    async def on_message(self, message):
        if not message.guild:
            return

        await self.process_commands(message)


async def getprefix(bot, message):
    if db_engine == "postgresql":
        try:
            data = await bot.db.fetchrow(
                "SELECT * FROM guild_data WHERE guild=$1", message.guild.id
            )
        except:
            return "**"

        if not data:
            return "**"
        return data["prefix"]
    
    elif db_engine == "sqlite3":
        try:
            cursor = await bot.db.execute(
                f"SELECT * FROM guild_data WHERE guild={message.guild.id}"
            )
            data = await cursor.fetchone()

            return data[2]
        except:
            return "**"


bot = MyBot(command_prefix="m.")
bot.remove_command(
    "help"
)  # If you are planning to make a subclassed help command comment this out or remove this line


async def create_db_pool():
    if db_engine == "postgresql":
        bot.db = await asyncpg.create_pool(**db_config)

        await bot.db.execute(
            """
			CREATE TABLE IF NOT EXISTS guild_data(
				id SERIAL PRIMARY KEY NOT NULL,
				guild BIGINT NOT NULL,
				prefix TEXT NOT NULL
			)
		"""
        )

        await bot.db.execute(
            """
			CREATE TABLE IF NOT EXISTS monitor(
				id SERIAL PRIMARY KEY NOT NULL,
				guild BIGINT NOT NULL,
				target BIGINT NOT NULL,
				mentor BIGINT NOT NULL,
				channel BIGINT NULL
			)
		"""
        )
    elif db_engine == "sqlite3":
        import aiosqlite

        db_name = "anyname"
        bot.db = await aiosqlite.connect(db_name + ".db")

        await bot.db.execute(
            """
			CREATE TABLE IF NOT EXISTS guild_data(
				id INTEGER PRIMARY KEY NOT NULL,
				guild INT NOT NULL,
				prefix TEXT NOT NULL
			)
		"""
        )


bot.loop.run_until_complete(create_db_pool())

for extenstion in extensions:
    try:
        bot.load_extension(extenstion)
        print(f"Extension {extenstion} loaded successfully.")
    except Exception as e:
        print(f"Failed to load {extenstion} {e}.")

dotenv.load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
