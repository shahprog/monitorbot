import discord
from discord.ext import commands


class Events(commands.Cog):
    """Bot event listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", guild.id
        )
        if not data:
            await self.bot.db.execute(
                "INSERT INTO guild_data(guild, prefix) VALUES($1, $2)", guild.id, "**"
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await self.bot.db.execute("DELETE FROM guild_data WHERE guild=$1", guild.id)
            print(f"Bot get kicked from {guild.name} and data deleted.")
        except:
            print(f"Something went wrong deleting a row {guild.id}")


def setup(bot):
    bot.add_cog(Events(bot))
