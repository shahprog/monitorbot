import discord
from discord.ext import commands, menus
import asyncpg
import asyncio
from random import randint

class MySource(menus.ListPageSource):
    def __init__(self, data, title: str):
        super().__init__(data, per_page=10)
        self.title = title

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(
            title=f"{self.title}", color=discord.Color.blurple()
        )
        description = "\n".join(
            f"{i+1}. {v}" for i, v in enumerate(entries, start=offset)
        )
        description = discord.utils.escape_mentions(description)
        embed.description = description
        # embed.set_thumbnail(url=ctx.guild.icon_url)
        return embed


class Monitor(commands.Cog):
    """Monitor related commands"""
    def __init__(self, bot):
        self.bot = bot

    async def add_monitors(self, monitors, ctx, channel_id):
        count = 0
        for monitor in monitors:
            data = await self.bot.db.fetchrow(
                "SELECT * FROM monitor WHERE target = $1 and mentor = $2 and guild=$3",
                monitor,
                ctx.author.id,
                ctx.guild.id
            )

            if data:
                pass
            else:
                count += 1
                await self.bot.db.execute(
                    "INSERT INTO monitor(target, mentor, guild, channel) VALUES($1, $2,$3, $4)",
                    monitor,
                    ctx.author.id,
                    ctx.guild.id,
                    channel_id,
                )
        return count

    @commands.group(invoke_without_command=True)
    async def monitor(self, ctx):
        """Monitor a member when they they go offline or come online you will get notified"""
        await ctx.send(f"Do `{ctx.prefix}help monitor` to get help")

    @monitor.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, members:commands.Greedy[discord.Member], channel: discord.TextChannel = None):
        """Monitor someone."""
        if channel is not None:
            channel_id = channel.id
        else:
            channel_id = None

        monitors = [member.id for member in members]

        num = await self.add_monitors(monitors, ctx, channel_id)

        if num > 0:
            await ctx.send(f'{num} new monitor created.')
        else:
            await ctx.send('No new monitor were created')

    @monitor.command()
    @commands.has_permissions(administrator=True)
    async def all(self, ctx, group:str='bot', channel: discord.TextChannel = None):
        """Monitor all member/bot in a server"""
        if channel is not None:
            bot = ctx.guild.get_member(self.bot.user.id)
            if not bot.permissions_in(channel).send_messages:
                return await ctx.send("Sorry! I cant send message on that channel. Use different channel or give me permission to send message on that channel.")
            else:
                channel_id = channel.id
        else:
            channel_id = None

        if group == 'bot':
            group = 'bots'
            monitors = [member.id for member in ctx.guild.members if member.bot == True]
        else:
            group = 'members (excluding bots)'
            monitors = [member.id for member in ctx.guild.members if member.bot == False]

        def check(m):
            valid = ['yes', 'no']
            if (m.author == ctx.author and m.channel == ctx.channel) and m.content.lower() in valid:
                return True
            return False

        question = await ctx.send(f'Are you sure you want to monitor `{len(monitors)}` {group}? Write yes or no in 60 seconds...')

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
        except:
            try:
                await question.delete()
            except:
                pass
            return await ctx.send('Cancelled!', delete_after=3)

        if message.content.lower() == 'yes':
            pass
        else:
            return await ctx.send('Cancelled')

        try:
            await message.delete()
            await question.delete()
        except:
            pass

        num = await self.add_monitors(monitors, ctx, channel_id)

        await ctx.send(f'{num} monitor created.')

    @monitor.command(name="list", aliases=['ls'])
    async def _ls(self, ctx):
        """View list of your monitors"""
        data = await self.bot.db.fetch(
            "SELECT * FROM monitor WHERE mentor = $1 and guild=$2", ctx.author.id, ctx.guild.id
        )

        if not data:
            return await ctx.send("You have no monitor right now in this guild.")

        unfiltered = [self.bot.get_user(row["target"]) for row in data]
        targets = [str(target) for target in unfiltered if target]

        if len(targets) < 1:
            return await ctx.send('You don\'t have any monitor right now.')

        pages = menus.MenuPages(source=MySource(targets, f'Monitor of {str(ctx.author)}'), clear_reactions_after=True)
        await pages.start(ctx)

    @monitor.command(name='delete', aliases=['del', 'remove', 'rm'])
    async def dl_(self, ctx, monitors:commands.Greedy[discord.Member]):
        """Delete monitors."""
        monitors = [member.id for member in monitors]

        done = 0
        undone = 0
        for monitor in monitors:
            data = await self.bot.db.fetchrow("SELECT * FROM monitor WHERE target = $1 and mentor = $2 and guild = $3", monitor, ctx.author.id, ctx.guild.id)
            if data:
                await self.bot.db.execute("DELETE FROM monitor WHERE target = $1 and mentor = $2 and guild = $3", monitor, ctx.author.id, ctx.guild.id)
                done += 1
            else:
                undone += 1
        await ctx.send(f'{done} monitor removed.')

    @monitor.command(aliases=['purge'])
    async def clear(self, ctx):
        """Delete all monitor in server you added."""
        await self.bot.db.execute("DELETE FROM monitor WHERE mentor = $1 and guild = $2", ctx.author.id, ctx.guild.id)

        await ctx.send('All the monitor you created in this server is now deleted.')

def setup(bot):
    bot.add_cog(Monitor(bot))
