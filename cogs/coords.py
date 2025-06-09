from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands


class Coords(commands.Cog, name="Coords"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="claim",
        description="Claim a coordinate"
    )
    async def claim(self, ctx: Context, *, arg) -> None:
        coords = []
        if "," in arg:
            coords = arg.replace(" ", "").split(",")
        elif ";" in arg:
            coords = arg.replace(" ", "").split(";")
        elif "x" in arg:
            coords = arg.replace(" ", "").split("x")
        elif " " in arg:
            coords = arg.split(" ")

        if len(coords) != 2:
            await ctx.reply(f"Please provide coordinates in the appropriate format: `x,y`, `x;y` , `x y`")
            return

        if coords[0] < 0 or coords[0] > 999 or coords[1] < 0 or coords[1] > 999:
            await ctx.reply(f"Coordinates should be between 0 and 999")
            return

        # Coords     Player       Timestamp             Expires
        await ctx.reply(f"Claiming coords: {coords[0]}, {coords[1]} - {ctx.message.author} - {datetime.now()} - {datetime.now() + 24}")

    @commands.hybrid_command(
        name="delete",
        description="Delete your claim on a coordinate"
    )
    async def delete(self, ctx: Context) -> None:
        self.bot.logger.info(f"Test log by: {ctx.message.author}")
        await ctx.reply("Test test")

    @commands.hybrid_command(
        name="extend",
        description="Extend your claim on a coordinate"
    )
    async def extend(self, ctx: Context) -> None:
        self.bot.logger.info(f"Test log by: {ctx.message.author}")
        await ctx.reply("Test test")


async def setup(bot) -> None:
    await bot.add_cog(Coords(bot))
