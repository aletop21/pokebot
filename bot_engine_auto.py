from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


class PokemonStatus(str, Enum):
    ALIVE = "alive"
    DEFEATED = "defeated"


@dataclass
class PokemonState:
    name: str
    level: Optional[int] = None
    battle_index: Optional[int] = None
    position: Optional[Tuple[int, int]] = None
    status: PokemonStatus = PokemonStatus.ALIVE


@dataclass
class CommandProfile:
    name: str
    commands: List[str] = field(default_factory=list)


@dataclass
class BallProfile:
    name: str
    item_position: Tuple[int, int]


@dataclass
class BotConfig:
    command_profile: CommandProfile
    default_ball: BallProfile
    ball_by_pokemon: Dict[str, BallProfile] = field(default_factory=dict)


class InputAdapter:
    """Abstraction over keyboard/mouse API to keep engine testable."""

    def click(self, x: int, y: int, right_click: bool = False) -> None:
        raise NotImplementedError

    def type_text(self, text: str) -> None:
        raise NotImplementedError


class BattleBotEngine:
    """Core automation logic for Tibia Pokemon battle + capture workflow.

    Flow:
    1. Receive current battle window snapshot.
    2. If a new pokemon appears, target the second battle entry.
    3. Execute configured command sequence.
    4. Track pokemon sprite coordinates while alive.
    5. When defeated, throw selected pokeball at last known coordinates.
    """

    def __init__(
        self,
        config: BotConfig,
        input_adapter: InputAdapter,
        battle_name_parser: Optional[Callable[[str], Tuple[str, Optional[int]]]] = None,
    ) -> None:
        self.config = config
        self.input = input_adapter
        self._parser = battle_name_parser or self._default_parse_name
        self._known: Dict[str, PokemonState] = {}
        self._active_target: Optional[str] = None

    @staticmethod
    def _default_parse_name(raw: str) -> Tuple[str, Optional[int]]:
        value = raw.strip()
        if "[" in value and value.endswith("]"):
            name, level_part = value.rsplit("[", 1)
            level_txt = level_part[:-1].strip()
            level = int(level_txt) if level_txt.isdigit() else None
            return name.strip().lower(), level
        return value.lower(), None

    def current_states(self) -> Dict[str, PokemonState]:
        return {k: v for k, v in self._known.items()}

    def update_cycle(
        self,
        battle_entries: Sequence[str],
        sprite_positions: Dict[str, Tuple[int, int]],
        battle_click_positions: Sequence[Tuple[int, int]],
    ) -> None:
        parsed_names = [self._parser(entry)[0] for entry in battle_entries]
        new_names = [name for name in parsed_names if name not in self._known]

        # Register and track all currently visible pokemon.
        for index, raw in enumerate(battle_entries):
            name, level = self._parser(raw)
            state = self._known.get(name)
            if state is None:
                self._known[name] = PokemonState(name=name, level=level, battle_index=index)
            else:
                state.battle_index = index
                state.status = PokemonStatus.ALIVE

            if name in sprite_positions:
                self._known[name].position = sprite_positions[name]

        if new_names and len(battle_entries) >= 2:
            self._start_combat_sequence(parsed_names[1], battle_click_positions)

        # Mark missing pokemon as defeated and capture.
        for name, state in self._known.items():
            if name not in parsed_names and state.status == PokemonStatus.ALIVE:
                state.status = PokemonStatus.DEFEATED
                self._throw_ball(name)

    def _start_combat_sequence(
        self,
        second_name: str,
        battle_click_positions: Sequence[Tuple[int, int]],
    ) -> None:
        self._active_target = second_name
        if len(battle_click_positions) >= 2:
            x, y = battle_click_positions[1]
            self.input.click(x, y, right_click=False)

        for cmd in self.config.command_profile.commands:
            self.input.type_text(cmd)

    def _choose_ball(self, pokemon_name: str) -> BallProfile:
        return self.config.ball_by_pokemon.get(pokemon_name, self.config.default_ball)

    def _throw_ball(self, pokemon_name: str) -> None:
        state = self._known.get(pokemon_name)
        if state is None or state.position is None:
            return

        ball = self._choose_ball(pokemon_name)
        bx, by = ball.item_position
        self.input.click(bx, by, right_click=True)

        tx, ty = state.position
        self.input.click(tx, ty, right_click=True)


class RecordingInputAdapter(InputAdapter):
    """Utility adapter for tests and dry runs."""

    def __init__(self) -> None:
        self.events: List[str] = []

    def click(self, x: int, y: int, right_click: bool = False) -> None:
        button = "right" if right_click else "left"
        self.events.append(f"click:{button}:{x}:{y}")

    def type_text(self, text: str) -> None:
        self.events.append(f"type:{text}")
