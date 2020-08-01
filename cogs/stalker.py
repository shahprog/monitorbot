import discord
from discord.ext import commands
import datetime
from timetils import Formatter
import pytz


class Stalker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.emoji_cache = {
            "online": discord.utils.get(self.bot.emojis, id=738392645965185095),
            "offline": discord.utils.get(self.bot.emojis, id=738392685206831117),
        }

        self.bot.colors = {
            "online": 0x00FF80,
            "idle": 0xF1CB02,
            "offline": 0xB6B6B6,
            "dnd": 0xF96A4B,
        }

    async def notify(self, status_from, status_to, row):
        guild: discord.Guild = self.bot.get_guild(row["guild"])
        mentor: discord.Member = guild.get_member(row["mentor"])
        target: discord.Member = guild.get_member(row["target"])
        channel: discord.TextChannel = discord.utils.get(
            guild.text_channels, id=row["channel"]
        )  # can be null
        last: datetime.datetime = row[
            "last_update"
        ]  # last status update datetime can be null

        tz_info = await self.bot.db.fetchrow(
            "SELECT * FROM user_tz WHERE userid = $1", mentor.id
        )
        if last is not None:
            updated = last
            current_time = datetime.datetime.now()
            delta = current_time - updated
        else:
            delta = None

        status_emoji = self.bot.emoji_cache[status_to]

        embed = discord.Embed(
            title=f"Status update of {target}",
            color=self.bot.colors[target.status.name],
        )
        description = f"{str(self.bot.emoji_cache[status_to])} {status_to}.\n\n"

        if delta:
            description += (
                f"**Was {status_from} for** : {Formatter().natural_delta(delta)} \n"
            )

        if tz_info and last:
            tz = pytz.timezone(tz_info["tz"])
            if status_to == "offline":
                description += f"**Gone offline** : {Formatter().natural_datetime(datetime.datetime.now((pytz.timezone(tz_info['tz']))))} \n"
            if status_to == "online":
                description += f"**Came online** : {Formatter().natural_datetime(datetime.datetime.now((pytz.timezone(tz_info['tz']))))} \n"

        embed.description = description

        if channel and mentor.guild_permissions.administrator:
            await channel.send(embed=embed)
        else:
            await mentor.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_status = before.status
        after_status = after.status

        online = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

        data = await self.bot.db.fetch(
            "SELECT * FROM monitor WHERE target = $1 and guild = $2",
            after.id,
            after.guild.id,
        )
        if not data:
            return

        if after_status in online and before_status in online:
            return

        embed = discord.Embed(title=f"Status update of {str(after)}")
        if after_status in online and before_status not in online:
            if data:
                for row in data:
                    await self.notify("offline", "online", row)

        if after_status not in online and before_status in online:
            if data:
                for row in data:
                    await self.notify("online", "offline", row)

        await self.bot.db.execute(
            "UPDATE monitor SET last_update = $1 WHERE mentor = $2",
            datetime.datetime.now(),
            data[0]["mentor"],
        )


def setup(bot):
    bot.add_cog(Stalker(bot))
