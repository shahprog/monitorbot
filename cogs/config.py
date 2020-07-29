import discord
from discord.ext import commands


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


def setup(bot):
    bot.add_cog(Config(bot))
