"""Stubs for the on-device `badgeware` module (editor / Pyright only)."""

from collections.abc import Callable
from typing import Any

def run(
    update: Callable[..., Any],
    init: Callable[..., Any] | None = None,
    on_exit: Callable[..., Any] | None = None,
) -> Any: ...

def clamp(value: float | int, low: float | int, high: float | int) -> float | int: ...

BG: Any
FG: Any
