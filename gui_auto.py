from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Tuple

from bot_engine_auto import BallProfile, BattleBotEngine, BotConfig, CommandProfile, RecordingInputAdapter


class AutoBotGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Tibia Pokemon Auto Bot")
        self.geometry("720x520")

        self.command_profile_name = tk.StringVar(value="default")
        self.commands_text = tk.StringVar(value="m12,m11,m10,tm1,mt4")
        self.default_ball_name = tk.StringVar(value="Ultra Ball")
        self.default_ball_position = tk.StringVar(value="100,100")

        self.special_map_rows: list[tuple[tk.StringVar, tk.StringVar]] = []

        self.engine: BattleBotEngine | None = None
        self.input_adapter = RecordingInputAdapter()

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Command Profile Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.command_profile_name, width=40).grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(container, text="Commands (comma-separated)").grid(row=1, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.commands_text, width=40).grid(row=1, column=1, sticky="ew", padx=8)

        ttk.Label(container, text="Default Pokeball Name").grid(row=2, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.default_ball_name, width=40).grid(row=2, column=1, sticky="ew", padx=8)

        ttk.Label(container, text="Default Ball Position (x,y)").grid(row=3, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.default_ball_position, width=40).grid(row=3, column=1, sticky="ew", padx=8)

        special_frame = ttk.LabelFrame(container, text="Pokemon-specific ball mapping")
        special_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        special_frame.columnconfigure(0, weight=1)
        special_frame.columnconfigure(1, weight=1)

        ttk.Button(special_frame, text="Add mapping", command=lambda: self._add_special_row(special_frame)).grid(row=0, column=0, sticky="w", padx=4, pady=4)

        controls = ttk.Frame(container)
        controls.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        ttk.Button(controls, text="Start", command=self.start_bot).pack(side=tk.LEFT)
        ttk.Button(controls, text="Run Demo Tick", command=self.run_demo_tick).pack(side=tk.LEFT, padx=6)
        ttk.Button(controls, text="Show Event Log", command=self.show_log).pack(side=tk.LEFT)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

    def _add_special_row(self, frame: ttk.LabelFrame) -> None:
        name_var = tk.StringVar()
        pos_var = tk.StringVar(value="120,120")
        row = len(self.special_map_rows) + 1

        ttk.Entry(frame, textvariable=name_var, width=24).grid(row=row, column=0, sticky="ew", padx=4, pady=2)
        ttk.Entry(frame, textvariable=pos_var, width=24).grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        self.special_map_rows.append((name_var, pos_var))

    def _parse_point(self, raw: str) -> Tuple[int, int]:
        x_str, y_str = [s.strip() for s in raw.split(",", 1)]
        return int(x_str), int(y_str)

    def _build_engine(self) -> BattleBotEngine:
        commands = [v.strip() for v in self.commands_text.get().split(",") if v.strip()]
        profile = CommandProfile(name=self.command_profile_name.get().strip() or "default", commands=commands)

        default_ball = BallProfile(
            name=self.default_ball_name.get().strip() or "Default Ball",
            item_position=self._parse_point(self.default_ball_position.get()),
        )

        ball_by_pokemon: Dict[str, BallProfile] = {}
        for name_var, pos_var in self.special_map_rows:
            pname = name_var.get().strip().lower()
            if not pname:
                continue
            ball_by_pokemon[pname] = BallProfile(name=f"{pname}-ball", item_position=self._parse_point(pos_var.get()))

        config = BotConfig(command_profile=profile, default_ball=default_ball, ball_by_pokemon=ball_by_pokemon)
        return BattleBotEngine(config=config, input_adapter=self.input_adapter)

    def start_bot(self) -> None:
        try:
            self.engine = self._build_engine()
        except ValueError as exc:
            messagebox.showerror("Invalid configuration", str(exc))
            return

        messagebox.showinfo("Bot Ready", "Bot configuration loaded. Use 'Run Demo Tick' for a dry-run cycle.")

    def run_demo_tick(self) -> None:
        if self.engine is None:
            self.start_bot()
            if self.engine is None:
                return

        self.engine.update_cycle(
            battle_entries=["Onix [55]", "Rhyperior [130]"],
            sprite_positions={"onix": (640, 370), "rhyperior": (670, 388)},
            battle_click_positions=[(900, 330), (900, 350)],
        )
        self.engine.update_cycle(
            battle_entries=["Onix [55]"],
            sprite_positions={"onix": (640, 370)},
            battle_click_positions=[(900, 330)],
        )
        messagebox.showinfo("Demo", "Demo cycle complete. Open log to inspect actions.")

    def show_log(self) -> None:
        if not self.input_adapter.events:
            messagebox.showinfo("Log", "No events yet.")
            return
        messagebox.showinfo("Action Log", "\n".join(self.input_adapter.events))


if __name__ == "__main__":
    app = AutoBotGUI()
    app.mainloop()
