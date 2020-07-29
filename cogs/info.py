import discord
from discord.ext import commands
from timetils import Formatter
import datetime
import sys

class Info(commands.Cog):
	"""Bot info commands."""
	def __init__(self, bot):
		self.bot = bot
		self.formatter = Formatter()


	@commands.command()
	@commands.is_owner()
	async def ping(self, ctx):
		"""Shows bot latency"""
		latency = int(self.bot.latency * 1000)

		await ctx.send(f"{latency}ms")

	@commands.command(aliases=['about', 'botinfo'])
	async def info(self, ctx):
		"""Shows bot info"""
		pyv = (
            str(sys.version_info[0])
            + "."
            + str(sys.version_info[1])
            + "."
            + str(sys.version_info[2])
        )
		lib = "discord.py"
		dpv = str(discord.__version__)
		owner = "Shahriyar#9770"
		cmds = len(self.bot.commands)
		shards = len(self.bot.shards)

		des = ""
		des += "**Owner** : " + owner + "\n"
		des += "**Lib** : " + lib + ", v" + dpv + "\n"
		des += "**Shards** : " + str(shards) + "\n"
		des += "**Python** : " + pyv + "\n"
		# des += "**Total commands** : " + str(cmds) + "\n"
		des += (
            "**Active since** : "
            + Formatter().natural_delta(datetime.datetime.utcnow() - self.bot.user.created_at) + " ago"
            + "\n"
        )
		des += "**Guilds** : " + str(len(self.bot.guilds)) + "\n"
		des += "**Users** : " + str(len(self.bot.users)) + "\n"

		des += "**Rebooted** : " + Formatter().natural_delta(datetime.datetime.utcnow() - self.bot.launch_time) + " ago \n"
        
		des += f"[Join Support Server](https://discord.gg/7SaE8v2) | [Invite bot](https://top.gg/bot/696975708907503636) | [Vote](https://top.gg/bot/696975708907503636/vote) | [Custom Commands](https://top.gg/bot/724847752449753140)"
        # des += "[![Discord Bots](https://top.gg/api/widget/696975708907503636.svg)](https://top.gg/bot/696975708907503636)"
		embed = discord.Embed(
            color=ctx.author.color,
            description=des,
            title=self.bot.user.name,
            timestamp=ctx.message.created_at,
        )
		embed.set_thumbnail(url=self.bot.user.avatar_url)

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))
