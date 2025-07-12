import time
import datetime

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

from utils.coordinate import Coordinate, CoordinateParseException, CoordinateClaimedException, CoordinateNotClaimedException

from CoordsTracker import CoordsTracker


class Coords(commands.Cog, name="Coords"):
    def __init__(self, bot: CoordsTracker) -> None:
        self.bot = bot
        self.check_expired_claims.start()

    def cog_unload(self):
        self.check_expired_claims.cancel()

    async def check_guild(self, ctx: Context):
        if not self.bot.database.check_guild(ctx.message.guild.id):
            await ctx.reply(f"There is no coordinate tracking set up in this server!\nStart by using `{ctx.prefix}setup`")
            return False
        return True

    async def check_coordinate(self, ctx, coordinate):
        start = int(time.time())
        end = start + 24 * 60 * 60
        try:
            coord = Coordinate.from_string(
                coordinate, ctx.message.author.id, start, end)
            return coord
        except CoordinateParseException as e:
            if e.split:
                await ctx.reply("Please provide coordinates in the appropriate format: `x,y`, `x;y` , `x y`")
                return False
            if e.bounds:
                await ctx.reply("Coordinates should be between `(0,0)` and `(999,999)`")
                return False

    async def update_overview(self):

        for guild in self.bot.database.get_all_guilds():
            if guild[3] == 0:
                continue
            data = self.bot.database.get_claimed_coords(guild[1])
            print(data)
            text = ""
            for coord in data:
                text += "" + Coordinate(*(coord[x] for x in (1, 2, 3, 5, 6))).format() + "\n"

            embed = discord.Embed(title="All claimed coords",
                                  color=self.bot.user.color,
                                  description="Claim a coord: `!claim x,y`")
            embed.add_field(
                name="Coords",
                value="`{:^8} - {:^15}`..\n..`{:^15} - {:^15}`\n{}".format(
                    "Coord", "Owner", "Timestamp", "Expires", text)
            )
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Select the buttons bellow to sort.")
            embed.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar)

            channel = await self.bot.fetch_channel(guild[3])

            try:
                msg = await channel.fetch_message(guild[4])
                await msg.edit(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            except discord.NotFound or discord.Forbidden:
                msg = await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
                self.bot.database.set_overview_message(guild[1], msg.id)

    @commands.hybrid_command(
        name="setup",
        description="Setup for the coordinate system"
    )
    async def setup(self, ctx: Context) -> None:
        guild = ctx.message.guild.id
        if not self.bot.database.check_guild(guild):
            self.bot.database.add_guild(guild)

        await ctx.reply(f"Setup succesful!\nTo add an overview channel, use `{ctx.prefix}channel`")

    @commands.hybrid_command(
        name="notify_channel",
        description="Choose a channel for the notifications to be send.",
        aliases=["notify"]
    )
    async def notify_channel(self, ctx: Context, channel: discord.TextChannel = None) -> None:

        guild = ctx.message.guild.id
        if not self.bot.database.check_guild(guild):
            self.bot.database.add_guild(guild)

        if channel is None:
            self.bot.database.set_notify_channel(guild, 0)
            await ctx.reply("Notifications are disabled!")
        else:
            self.bot.database.set_notify_channel(guild, channel.id)
            await ctx.reply(f"{channel.mention} will be used for the notifications!")

    @commands.hybrid_command(
        name="overview_channel",
        description="Choose a channel for the notifications to be send.",
        aliases=[""]
    )
    async def overview_channel(self, ctx: Context, channel: discord.TextChannel = None) -> None:

        guild = ctx.message.guild.id
        if not self.bot.database.check_guild(guild):
            self.bot.database.add_guild(guild)

        if channel is None:
            self.bot.database.set_overview_channel(guild, 0)
            await ctx.reply("Overview is disabled!")
        else:
            self.bot.database.set_overview_channel(guild, channel.id)
            await ctx.reply(f"{channel.mention} will be used for the overview!")
            await self.update_overview()

    @commands.hybrid_command(
        name="claim",
        description="Claim a coordinate"
    )
    async def claim(self, ctx: Context, *, coordinate) -> None:

        if not await self.check_guild(ctx):
            return

        coord = await self.check_coordinate(ctx, coordinate)
        if not coord:
            return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")
        try:
            self.bot.database.claim_coord(coord, ctx.message.guild.id)
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is already claimed. It expires at <t:{e.end}:f>")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate `({coord.x},{coord.y})` claimed! Claim expires at <t:{coord.end}:f>")

        await self.update_overview()

    @commands.hybrid_command(
        name="delete",
        description="Delete your claim on a coordinate",
        aliases=["release"]
    )
    # @commands.check(check_guild)
    async def delete(self, ctx: Context, *, coordinate) -> None:

        if not await self.check_guild(ctx):
            return

        coord = await self.check_coordinate(ctx, coordinate)
        if not coord:
            return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")

        try:
            self.bot.database.release_coord(coord, ctx.message.guild.id)

        except CoordinateNotClaimedException as e:
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you!\nClaim it using `{ctx.prefix}claim {e.coord}`")
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you.\nWait until the previous claim expires at <t:{e.end}:f>, then claim it using `{ctx.prefix}claim {e.coord}`")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate `({coord.x},{coord.y})` released!")
        await self.update_overview()

    @commands.hybrid_command(
        name="extend",
        description="Extend your claim on a coordinate"
    )
    # @commands.check(check_guild)
    async def extend(self, ctx: Context, *, coordinate) -> None:

        if not await self.check_guild(ctx):
            return

        coord = await self.check_coordinate(ctx, coordinate)
        if not coord:
            return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")

        try:
            self.bot.database.extend_coord(coord, ctx.message.guild.id)

        except CoordinateNotClaimedException as e:
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you!\nClaim it using `{ctx.prefix}claim {e.coord}`")
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you.\nWait until the previous claim expires, then claim it using `!claim {e.coord}`")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate claim on `({coord.x},{coord.y})` extended until <t:{coord.end}:f>!")
        await self.update_overview()

    @commands.hybrid_command(
        name="show",
        description="show all coordinates claimed",
        aliases=["view"]
    )
    async def show(self, ctx: Context, *, filter="") -> None:

        if not await self.check_guild(ctx):
            return

        print(ctx.author.mention)

        data = self.bot.database.get_claimed_coords(ctx.message.guild.id)
        print(data)
        text = ""
        for coord in data:
            text += "" + Coordinate(*(coord[x] for x in (1, 2, 3, 5, 6))).format() + "\n"

        embed = discord.Embed(title="All claimed coords", color=ctx.guild.me.color,
                              description="Claim a coord: `!claim x,y`")
        embed.add_field(
            name="Coords",
            value="`{:^8} - {:^15}`..\n..`{:^15} - {:^15}`\n{}".format(
                "Coord", "Owner", "Timestamp", "Expires", text)
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Select the buttons bellow to sort.")
        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar)

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.hybrid_command(
        name="overview",
        description="Send the overview message",
        aliases=[]
    )
    async def overview(self, ctx: Context) -> None:

        if not await self.check_guild(ctx):
            return

        await self.update_overview()

    @tasks.loop(seconds=10.0)
    async def check_expired_claims(self):
        modified = False
        expired = self.bot.database.get_expiring()
        for coord in expired:
            self.bot.database.set_expired(coord[0])
            channel = await self.bot.fetch_channel(coord[11])
            await channel.send(f"<@{coord[3]}> Claim on `({coord[1]},{coord[2]})` expired!")
            modified = True

        notify = self.bot.database.get_notify()
        for coord in notify:
            self.bot.database.set_notify(coord[0])
            channel = await self.bot.fetch_channel(coord[11])
            await channel.send(f"<@{coord[3]}> Claim on `({coord[1]},{coord[2]})` is about to expire in <t:{coord[6] - 60 * 60 * 23}:R>!")
            modified = True

        if modified:
            await self.update_overview()


async def setup(bot: CoordsTracker) -> None:
    await bot.add_cog(Coords(bot))
