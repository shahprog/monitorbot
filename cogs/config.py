import discord
from discord.ext import commands
import pytz


class Config(commands.Cog):
    """Server configuration"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str):
        """Change prefix of bot"""
        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", ctx.guild.id
        )
        if not data:
            await self.bot.db.execute(
                "INSERT INTO guild_data(guild, prefix) VALUES($1, $2)",
                ctx.guild.id,
                "**",
            )

        await self.bot.db.execute(
            "UPDATE guild_data SET prefix=$1 WHERE guild=$2",
            str(new_prefix),
            ctx.guild.id,
        )
        await ctx.send(f"Prefix changed to {new_prefix}.")

    @commands.command()
    async def settz(self, ctx, timezone: str):
        """Set timezone to get exact status info"""
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            return await ctx.send("Invalid timezone. List of valid timezone <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>")

        data = await self.bot.db.fetchrow("SELECT * FROM user_tz WHERE userid = $1", ctx.author.id)

        if data:
            await self.bot.db.execute("UPDATE user_tz SET tz=$1 WHERE id=$2", timezone, data['id'])
        else:
            await self.bot.db.execute("INSERT INTO user_tz(userid, tz) VALUES($1, $2)", ctx.author.id, timezone)

        await ctx.send('Timezone updated successfully.')


def setup(bot):
    bot.add_cog(Config(bot))
