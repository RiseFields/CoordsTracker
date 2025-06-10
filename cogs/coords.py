import time
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands

from utils.coordinate import Coordinate, CoordinateParseException, CoordinateClaimedException


class Coords(commands.Cog, name="Coords"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="claim",
        description="Claim a coordinate"
    )
    async def claim(self, ctx: Context, *, coordinate) -> None:
        start = int(time.time())
        end = start + 24*60*60
        try:
            coords = Coordinate.from_string(
                coordinate, ctx.message.author.id, start, end)
        except CoordinateParseException as e:
            if e.split:
                await ctx.reply(f"Please provide coordinates in the appropriate format: `x,y`, `x;y` , `x y`")
                return
            if e.bounds:
                await ctx.reply(f"Coordinates should be between `(0,0)` and `(999,999)`")
                return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")

        try:
            self.bot.database.claim_coord(coords)
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is already claimed. It expires at <t:{e.end}:f>")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate `({coords.x},{coords.y})` claimed! Claim expires at <t:{end}:f>")

    @commands.hybrid_command(
        name="delete",
        description="Delete your claim on a coordinate",
        aliases=["release"]
    )
    async def delete(self, ctx: Context, *, coordinate) -> None:
        start = int(time.time())
        end = start + 24*60*60
        try:
            coords = Coordinate.from_string(
                coordinate, ctx.message.author.id, start, end)
        except CoordinateParseException as e:
            if e.split:
                await ctx.reply(f"Please provide coordinates in the appropriate format: `x,y`, `x;y` , `x y`")
                return
            if e.bounds:
                await ctx.reply(f"Coordinates should be between `(0,0)` and `(999,999)`")
                return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")

        try:
            self.bot.database.release_coord(coords.x, coords.y, coords.user)
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you.\nWait until the previous claim expires, then claim it using `!claim {e.coord}`")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate `({coords.x},{coords.y})` released!")

    @commands.hybrid_command(
        name="extend",
        description="Extend your claim on a coordinate"
    )
    async def extend(self, ctx: Context, *, coordinate) -> None:
        start = int(time.time())
        end = start + 24*60*60
        try:
            coords = Coordinate.from_string(
                coordinate, ctx.message.author.id, start, end)
        except CoordinateParseException as e:
            if e.split:
                await ctx.reply(f"Please provide coordinates in the appropriate format: `x,y`, `x;y` , `x y`")
                return
            if e.bounds:
                await ctx.reply(f"Coordinates should be between `(0,0)` and `(999,999)`")
                return

        # Coords     Player       Timestamp             Expires
        # row_format ="{:>15}" * (len(teams_list) + 1)
        # print(row_format.format("", *teams_list))
        # for team, row in zip(teams_list, data):
        #     print(row_format.format(team, *row))
        # await ctx.reply(f"Claiming coords: {x}, {y} - {ctx.message.author} - <t:{start}:f> - <t:{end}:f>")

        try:
            self.bot.database.extend_coord(
                coords.x, coords.y, coords.user, end)
        except CoordinateClaimedException as e:
            print(e)
            await ctx.reply(f"Coordinate `{e.coord}` is not claimed by you.\nWait until the previous claim expires, then claim it using `!claim {e.coord}`")
        except Exception as e:
            raise e
        else:
            await ctx.reply(f"Coordinate claim on `({coords.x},{coords.y})` extended until <t:{end}:f>!")

    @commands.hybrid_command(
        name="show",
        description="show all coordinates claimed",
        aliases=["view"]
    )
    async def show(self, ctx: Context, *, filter="") -> None:

        data = self.bot.database.get_all_coords()
        print(data)
        text = ""
        for coord in data:
            text += "" + Coordinate(*coord[1::]).format() + "\n"

        embed = discord.Embed(title=f"All claimed coords", color=ctx.guild.me.color,
                              description=f"Claim a coord: `!claim x,y`")
        embed.add_field(
            name="Coords",
            value="`{:^8} - {:^15}`..\n..`{:^15} - {:^15}`\n{}".format(
                "Coord", "Owner", "Timestamp", "Expires", text)
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Select the buttons bellow to sort.")
        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar)

        await ctx.reply(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Coords(bot))
