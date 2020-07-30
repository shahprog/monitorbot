import discord
from discord.ext import commands
import asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        print("Getting ready to shutdown")
        await self.bot.db.close()
        print("Db connection closed")
        print("Logging out")
        await ctx.send("Logging out.")
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def disable(self, ctx, command_or_cog):
        """Disable command/cog."""
        cmd = self.bot.get_command(command_or_cog)
        if cmd is None:
            try:
                cog = self.bot.cogs[command_or_cog]
            except:
                return await ctx.send(
                    f"No command or cog found with the name `{command_or_cog}`"
                )

            for command_or_group in cog.get_commands():
                if isinstance(command_or_group, commands.group):
                    for command in command_or_group:
                        command.enabled = False
                    command_or_group.enabled = False

                if isinstance(command_or_group, commands.Command):
                    command_or_group.enabled = False

            return await ctx.send(f"Cog {command_or_cog} has been disabled.")
        else:
            if isinstance(cmd, commands.group):
                for command in cmd:
                    command.enabled = False
                cmd.enabled = False
                what = "Group"

            if isinstance(cmd, commands.Command):
                cmd.enabled = False
            await ctx.send(f"{what} {cmd} has been disabled.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def enable(self, ctx, command_or_cog):
        """Disable command/cog."""
        cmd = self.bot.get_command(command_or_cog)
        if cmd is None:
            try:
                cog = self.bot.cogs[command_or_cog]
            except:
                return await ctx.send(
                    f"No command or cog found with the name `{command_or_cog}`"
                )

            for command_or_group in cog.get_commands():
                if isinstance(command_or_group, commands.group):
                    for command in command_or_group:
                        command.enabled = True
                    command_or_group.enabled = True

                if isinstance(command_or_group, commands.Command):
                    command_or_group.enabled = True

            return await ctx.send(f"Cog {command_or_cog} has been disabled.")
        else:
            if isinstance(cmd, commands.group):
                for command in cmd:
                    command.enabled = True
                cmd.enabled = True
                what = "Group"

            if isinstance(cmd, commands.Command):
                cmd.enabled = True
            await ctx.send(f"{what} {cmd} has been disabled.")


def setup(bot):
    bot.add_cog(Admin(bot))
