import discord
from discord.ext import commands
import asyncpg
import asyncio
from random import randint
import datetime
from timetils import Formatter

class Stalker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.emoji_cache = {
                        'online' : discord.utils.get(self.bot.emojis, id=738392645965185095), 
                        'offline' : discord.utils.get(self.bot.emojis, id=738392685206831117) 
                    }

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

        embed = discord.Embed(
            title = f"Status update of {str(after)}"
            )
        if after_status in online and before_status not in online:
            if data:
                for row in data:
                    guild = self.bot.get_guild(row["guild"])
                    mentor = guild.get_member(row["mentor"])
                    target = guild.get_member(row["target"])
                    channel = discord.utils.get(guild.text_channels, id=row["channel"])
                    last = row['last_update']

                    if last is None:
                        msg = ""
                    else:
                        now = datetime.datetime.now()
                        delta = now - last

                        msg = "\n"
                        msg += "🕙 | Was offline for : " + Formatter().natural_delta(delta) + "\n"

                    try:
                        if channel and mentor.guild_permissions.administrator == True:
                            embed.description = f"{str(self.bot.emoji_cache['online'])} | {str(target)} is now online. \n{msg}"
                            await channel.send(embed=embed)
                        else:
                            embed.description = f"{str(self.bot.emoji_cache['online'])} | {str(target)} is now online. \n{msg}"
                            await mentor.send(embed=embed)

                        await self.bot.db.execute("UPDATE monitor SET last_update = $1 WHERE id=$2", datetime.datetime.now(), row['id'])
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
                    last = row['last_update']

                    if last is None:
                        msg = ""
                    else:
                        now = datetime.datetime.now()
                        delta = now - last
                        
                        msg = "\n"
                        msg += "🕙 | Was online for : " + Formatter().natural_delta(delta) + "\n"

                    try:
                        if channel and mentor.guild_permissions.administrator == True:
                            embed.description = f"{str(self.bot.emoji_cache['offline'])} | {str(target)} is now offline. \n{msg}"
                            await channel.send(embed=embed)
                        else:
                            embed.description = f"{str(self.bot.emoji_cache['offline'])} | {str(target)} is now offline. \n{msg}"
                            await mentor.send(embed=embed)

                        await self.bot.db.execute("UPDATE monitor SET last_update = $1 WHERE id=$2", datetime.datetime.now(), row['id'])
                    except Exception as e:
                        print(e)
                        await self.bot.db.execute(
                            "DELETE FROM monitor WHERE target = $1 and mentor = $2",
                            row["target"],
                            row["mentor"],
                        )

def setup(bot):
    bot.add_cog(Stalker(bot))