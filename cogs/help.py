import discord
import math
import asyncio
from discord.ext import commands


class MyHelpCommand(commands.HelpCommand):

	def get_command_help(self, command, grp):
		if command.hidden or command.enabled == False:
			return ""
		
		msg = ""

		if command.signature:
			msg += f'{self.clean_prefix}{grp}{command.qualified_name} {command.signature}\n'
		else:
			msg += f'{self.clean_prefix}{grp}{command.qualified_name}\n'
		if command.help:
			msg += f'`{command.help.splitlines()[0]}`\n'

		return msg

	def get_group_help(self, group):
		if group.hidden or group.enabled == False:
			return ""

		msg = ""

		msg += self.get_command_help(group, '')

		for command in list(group.commands)[::-1]:
			grp = group.qualified_name + " "
			msg += self.get_command_help(command, "")

		return msg

	def get_cog_help(self, cog):
		cmds = [command for command in cog.get_commands() if command.hidden == False]

		if len(cmds) < 1:
			return ""

		msg = ""
		msg += f"__{cog.qualified_name}__\n"
		msg += f"`{cog.description}`\n"

		for command in cog.get_commands():
			if isinstance(command, commands.Group):
				msg += self.get_group_help(command)
			else:
				msg += self.get_command_help(command, "")

		return msg

	async def send_bot_help(self, mapping):
		ctx = self.context
		pre = self.clean_prefix

		cogs = [cog for cog in ctx.bot.cogs.values() if len([command for command in cog.get_commands() if command.hidden == False]) > 0]

		msg = ""

		for cog in cogs:
			if cog.qualified_name == "Help":
				pass
			else:
				msg += f'__{cog.qualified_name}__\n`{cog.description}`\n\n'

		embed = discord.Embed(
			title = 'Help for Monitor bot',
			description = f'Do `{pre}help <category>` to get help on a category.\n\n'
			)
		embed.description += msg	
		await ctx.send(embed=embed)

	# Main Help
	async def send_cog_help(self, cog):
		ctx = self.context
		pre = self.clean_prefix

		msg = ""
		msg += self.get_cog_help(cog)		

		embed = discord.Embed(
			title = f'Help for category `{cog.qualified_name}`',
			description = msg
		)

		await ctx.send(embed=embed)

	# Command Help
	async def send_command_help(self, command):
		ctx = self.context
		pre = self.clean_prefix

		msg = ""
		msg += self.get_command_help(command, "")

		embed = discord.Embed(
			title = f'Help for command `{command}`',
			description = msg
		)

		await ctx.send(embed=embed)

	# Group Help
	async def send_group_help(self, group):
		ctx = self.context
		pre = self.clean_prefix

		msg = ""
		msg += self.get_group_help(group)

		embed = discord.Embed(
			title = f'Help for group `{group.qualified_name}`',
			description = msg
		)

		await ctx.send(embed=embed)

class Help(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.client._original_help_command = client.help_command
		client.help_command = MyHelpCommand()
		client.help_command.cog = self

	def cog_unload(self):
		self.client.help_command = self.client._original_help_command


def setup(client):
	client.add_cog(Help(client))
