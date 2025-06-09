import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands


class Test(commands.Cog, name="test"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="testcommand",
        description="This is a test command."
    )
    async def testcommand(self, ctx: Context) -> None:
        self.bot.logger.info(f"Test log by: {ctx.message.author}")
        await ctx.reply("Test test")

    @app_commands.command()
    async def test2(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test test")


async def setup(bot) -> None:
    await bot.add_cog(Test(bot))
