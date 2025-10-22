# Boost-Hawk

Boost-Hawk is a Discord bot that tracks Nitro boosting activity, logs boost
changes, and automatically manages a "Double Booster" role for members with two
tracked boosts.

## Features

- Detects when members start or stop boosting the server via `on_member_update`.
- Logs boost events to a configurable text channel.
- Tracks booster counts with a persistent JSON store.
- Automatically assigns and removes a "Double Booster" role when a member has
  two or more boosts recorded.
- Provides administrative commands to override tracked boost counts.

## Requirements

- Python 3.10+
- [discord.py](https://discordpy.readthedocs.io/en/stable/) 2.x

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

Copy `config.json.example` to `config.json` and update the values with your
Discord configuration:

```json
{
  "token": "YOUR_BOT_TOKEN",
  "guild_id": 123456789012345678,
  "log_channel_id": 234567890123456789,
  "double_role_id": 345678901234567890
}
```

> **Note:** Keep `config.json` private. The file is ignored by Git via
> `.gitignore` and should never be committed.

## Usage

Run the bot with:

```bash
python bot.py
```

On startup the bot loads persisted boost data from `boosters.json`. The file is
created automatically after the first change to the boost tracker.

### Commands

- `!setboosts @member <count>` — Administrators can override the number of
  boosts attributed to a member. Setting `count` to `0` clears the record.
- `!myboosts` — Users can check how many boosts are currently tracked for them.

## Development

A `requirements.txt` file is provided for convenience:

```
discord.py>=2.3.2,<3.0.0
```

Feel free to extend the bot with additional logging, leaderboards, or management
commands tailored to your community.
