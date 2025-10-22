"""State management helpers for tracking Discord server boosters."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict


class BoostTracker:
    """Keep track of how many boosts a member contributes."""

    def __init__(self, storage_path: str = "boosters.json") -> None:
        self._storage_path = Path(storage_path)
        self._lock = asyncio.Lock()
        self._boosters: Dict[int, int] = {}

    async def load(self) -> None:
        """Load tracker state from disk if a storage file exists."""

        async with self._lock:
            if not self._storage_path.exists():
                self._boosters = {}
                return

            with self._storage_path.open("r", encoding="utf-8") as fp:
                try:
                    data = json.load(fp)
                except json.JSONDecodeError:
                    data = {}

            self._boosters = {
                int(member_id): int(count)
                for member_id, count in data.items()
            }

    async def save(self) -> None:
        """Persist tracker state to disk."""

        async with self._lock:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with self._storage_path.open("w", encoding="utf-8") as fp:
                json.dump(self._boosters, fp, indent=2, sort_keys=True)

    async def set_boosts(self, member_id: int, count: int) -> None:
        """Record ``count`` boosts for ``member_id``."""

        async with self._lock:
            if count <= 0:
                self._boosters.pop(member_id, None)
            else:
                self._boosters[member_id] = count

        await self.save()

    async def ensure_default(self, member_id: int, default: int) -> int:
        """Ensure a default boost count for ``member_id`` exists.

        Returns the resulting boost count.
        """

        async with self._lock:
            current = self._boosters.get(member_id, 0)
            if current >= default:
                return current

            if default <= 0:
                self._boosters.pop(member_id, None)
                result = 0
            else:
                self._boosters[member_id] = default
                result = default

        await self.save()
        return result

    async def get_boosts(self, member_id: int) -> int:
        async with self._lock:
            return self._boosters.get(member_id, 0)

    async def all_boosters(self) -> Dict[int, int]:
        async with self._lock:
            return dict(self._boosters)
