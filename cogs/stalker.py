import discord
from discord.ext import commands
import asyncpg
import asyncio
from random import randint


class Stalker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_status = before.status
        after_status = after.status

        after_status_name = after_status.name
        before_status_name = before_status.name

        online = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

        # online_name = [name.name for name in online]

        data = await self.bot.db.fetch(
            "SELECT * FROM monitor WHERE target = $1 and guild = $2",
            after.id,
            after.guild.id,
        )
        if not data:
            return

        if after_status in online and before_status in online:
            return

        if after_status in online and before_status not in online:
            if data:
                for row in data:
                    guild = self.bot.get_guild(row["guild"])
                    mentor = guild.get_member(row["mentor"])
                    target = guild.get_member(row["target"])
                    channel = discord.utils.get(guild.text_channels, id=row["channel"])
                    try:
                        if channel and mentor.guild_permissions.administrator == True:
                            await channel.send(f"🍏 {str(target)} is now online. ")
                        else:
                            await mentor.send(f"🍏 {str(target)} is now online. ")
                    except Exception as e:
                        print(e)
                        await self.bot.db.execute(
                            "DELETE FROM monitor WHERE target = $1 and mentor = $2",
                            row["target"],
                            row["mentor"],
                        )

        if after_status not in online and before_status in online:
            if data:
                for row in data:
                    guild = self.bot.get_guild(row["guild"])
                    mentor = guild.get_member(row["mentor"])
                    target = guild.get_member(row["target"])
                    channel = discord.utils.get(guild.text_channels, id=row["channel"])
                    try:
                        if channel and mentor.guild_permissions.administrator == True:
                            await channel.send(f"🍎 {str(target)} is now offline.")
                        else:
                            await mentor.send(f"🍎 {str(target)} is now offline.")
                    except Exception as e:
                        print(e)
                        await self.bot.db.execute(
                            "DELETE FROM monitor WHERE target = $1 and mentor = $2",
                            row["target"],
                            row["mentor"],
                        )

def setup(bot):
    bot.add_cog(Stalker(bot))