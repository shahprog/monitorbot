import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    """Error handler"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{error.param.name} is a required argument.")

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Bad argument.")

        if isinstance(error, commands.CommandNotFound):
            pass

        if isinstance(error, commands.NotOwner):
            pass

        if isinstance(error, commands.MissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "permissions"
                isare = "are"
            else:
                sorno = "permission"
                isare = "is"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno} {isare} required to execute this command."
            )

        if isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send("🧠")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
