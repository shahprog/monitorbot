import dbl
from discord.ext import commands, tasks
import os

import asyncio


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.getenv("DBL")  # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth=os.getenv('WEBHOOK_AUTH'), webhook_port=5000)
        self.bot.dblpy = self.dblpy
        self.bot.token = self.token

    # The decorator below will work only on discord.py 1.1.0+
    # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats())

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        try:
            await self.dblpy.post_guild_count()
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

        # if you are not using the tasks extension, put the line below

        await asyncio.sleep(1800)

    # @commands.Cog.listener()
    # async def on_dbl_vote(self, data):
    #     print(data)


def setup(bot):
    bot.add_cog(TopGG(bot))