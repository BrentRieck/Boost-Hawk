"""Discord bot that tracks server boosts and manages a double booster role."""

from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from boost_tracker import BoostTracker
from config import BotConfig, ConfigError, load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoostHawkBot(commands.Bot):
    """Bot implementation that monitors boosting activity."""

    def __init__(self, config: BotConfig, tracker: BoostTracker):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        intents.presences = True

        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.tracker = tracker
        self.guild: Optional[discord.Guild] = None

    async def setup_hook(self) -> None:
        await self.tracker.load()
        logger.info("Loaded booster state: %s", await self.tracker.all_boosters())

    async def on_ready(self) -> None:
        self.guild = self.get_guild(self.config.guild_id)
        if self.guild is None:
            logger.warning(
                "Bot is connected but not a member of guild %s.",
                self.config.guild_id,
            )
        logger.info("Boost Hawk connected as %s", self.user)

    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if before.guild.id != self.config.guild_id:
            return

        if not before.premium_since and after.premium_since:
            await self._handle_boost_added(after)
        elif before.premium_since and not after.premium_since:
            await self._handle_boost_removed(after)

    async def _handle_boost_added(self, member: discord.Member) -> None:
        logger.info("Boost added by %s", member)
        count = await self.tracker.ensure_default(member.id, 1)
        await self._update_double_role(member, count)
        await self._log_event(
            f"🎉 {member.mention} has boosted the server!"
        )

    async def _handle_boost_removed(self, member: discord.Member) -> None:
        logger.info("Boost removed by %s", member)
        await self.tracker.set_boosts(member.id, 0)
        await self._update_double_role(member, 0)
        await self._log_event(
            f"💔 {member.mention} has stopped boosting the server."
        )

    async def _update_double_role(
        self, member: discord.Member, boost_count: int
    ) -> None:
        role = member.guild.get_role(self.config.double_role_id)
        if role is None:
            logger.warning("Double booster role %s not found", self.config.double_role_id)
            return

        has_role = role in member.roles
        if boost_count >= 2 and not has_role:
            await member.add_roles(role, reason="Boost Hawk double booster automation")
        elif boost_count < 2 and has_role:
            await member.remove_roles(
                role, reason="Boost Hawk double booster automation"
            )

    async def _log_event(self, message: str) -> None:
        guild = self.guild or self.get_guild(self.config.guild_id)
        if guild is None:
            logger.warning("Cannot log event; guild not available")
            return

        channel = guild.get_channel(self.config.log_channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            logger.warning(
                "Cannot log event; channel %s missing or not a text channel",
                self.config.log_channel_id,
            )
            return

        await channel.send(message)


bot_instance: Optional[BoostHawkBot] = None


def _require_bot() -> BoostHawkBot:
    if bot_instance is None:
        raise RuntimeError("Bot has not been initialised yet.")
    return bot_instance


@commands.command(name="setboosts")
@commands.has_permissions(administrator=True)
async def set_boosts(ctx: commands.Context, member: discord.Member, count: int) -> None:
    bot = _require_bot()
    await bot.tracker.set_boosts(member.id, count)
    await bot._update_double_role(member, count)
    await ctx.send(f"{member.mention} now has {count} boost(s) tracked.")


@commands.command(name="myboosts")
async def my_boosts(ctx: commands.Context) -> None:
    bot = _require_bot()
    count = await bot.tracker.get_boosts(ctx.author.id)
    await ctx.send(f"You currently have {count} tracked boost(s).")


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:  # pragma: no cover - configuration errors at startup
        logger.error("Unable to load configuration: %s", exc)
        raise SystemExit(1) from exc

    tracker = BoostTracker()
    bot = BoostHawkBot(config=config, tracker=tracker)
    global bot_instance
    bot_instance = bot

    bot.add_command(set_boosts)
    bot.add_command(my_boosts)

    bot.run(config.token)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
