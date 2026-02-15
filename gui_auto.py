from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Tuple

from bot_engine_auto import BallProfile, BattleBotEngine, BotConfig, CommandProfile, RecordingInputAdapter


class AutoBotGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Tibia Pokemon Auto Bot")
        self.geometry("860x620")
        self.minsize(820, 580)
        self.geometry("720x520")

        self.command_profile_name = tk.StringVar(value="default")
        self.commands_text = tk.StringVar(value="m12,m11,m10,tm1,mt4")
        self.default_ball_name = tk.StringVar(value="Ultra Ball")
        self.default_ball_position = tk.StringVar(value="100,100")
        self.hover_position = tk.StringVar(value="Mouse: x=0, y=0")

        # Each row: {name_var, pos_var, frame, row_index}
        self.special_map_rows: list[dict[str, object]] = []

        self.special_map_rows: list[tuple[tk.StringVar, tk.StringVar]] = []

        self.engine: BattleBotEngine | None = None
        self.input_adapter = RecordingInputAdapter()

        self._setup_style()
        self._build_layout()
        self._start_mouse_tracker()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("SubTitle.TLabel", font=("Segoe UI", 10), foreground="#455a64")
        style.configure("Section.TLabelframe", padding=10)
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", padding=(10, 6))
        style.configure("Hint.TLabel", foreground="#37474f")

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Tibia Pokémon Auto Bot", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Hover-to-confirm mapping • configurable commands • per-pokémon ball mapping",
            style="SubTitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        hover_panel = ttk.LabelFrame(root, text="Live Hover Mapping", style="Section.TLabelframe")
        hover_panel.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        hover_panel.columnconfigure(0, weight=1)
        hover_panel.columnconfigure(1, weight=1)

        ttk.Label(hover_panel, textvariable=self.hover_position, style="Hint.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(
            hover_panel,
            text="Use hover for default ball position",
            style="Primary.TButton",
            command=self._apply_hover_to_default,
        ).grid(row=0, column=1, sticky="e")
        ttk.Label(
            hover_panel,
            text="Move your mouse over the exact game slot/target and press a 'Use Hover' button to save coordinates.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        config = ttk.LabelFrame(root, text="Combat Configuration", style="Section.TLabelframe")
        config.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        config.columnconfigure(1, weight=1)

        ttk.Label(config, text="Command Profile Name").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(config, textvariable=self.command_profile_name).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Label(config, text="Commands (comma-separated)").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(config, textvariable=self.commands_text).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Label(config, text="Default Pokéball Name").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(config, textvariable=self.default_ball_name).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=3)

        default_row = ttk.Frame(config)
        default_row.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=3)
        default_row.columnconfigure(0, weight=1)

        ttk.Label(config, text="Default Ball Position (x,y)").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(default_row, textvariable=self.default_ball_position).grid(row=0, column=0, sticky="ew")
        ttk.Button(default_row, text="Use Hover", command=self._apply_hover_to_default).grid(row=0, column=1, padx=(6, 0))

        mappings = ttk.LabelFrame(root, text="Pokémon-specific Ball Mapping", style="Section.TLabelframe")
        mappings.grid(row=3, column=0, sticky="nsew")
        mappings.columnconfigure(0, weight=2)
        mappings.columnconfigure(1, weight=2)
        mappings.columnconfigure(2, weight=1)
        mappings.rowconfigure(2, weight=1)

        ttk.Label(mappings, text="Pokemon Name", style="Hint.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(mappings, text="Ball Position (x,y)", style="Hint.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Button(mappings, text="Add mapping", command=lambda: self._add_special_row(mappings)).grid(row=0, column=2, sticky="e")

        self.mapping_rows_frame = ttk.Frame(mappings)
        self.mapping_rows_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.mapping_rows_frame.columnconfigure(0, weight=2)
        self.mapping_rows_frame.columnconfigure(1, weight=2)

        controls = ttk.Frame(root)
        controls.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(controls, text="Start", style="Primary.TButton", command=self.start_bot).pack(side=tk.LEFT)
        ttk.Button(controls, text="Run Demo Tick", style="Primary.TButton", command=self.run_demo_tick).pack(side=tk.LEFT, padx=8)
        ttk.Button(controls, text="Show Event Log", style="Primary.TButton", command=self.show_log).pack(side=tk.LEFT)

    def _start_mouse_tracker(self) -> None:
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        self.hover_position.set(f"Mouse: x={x}, y={y}")
        self.after(120, self._start_mouse_tracker)

    def _current_hover_point(self) -> Tuple[int, int]:
        return self.winfo_pointerx(), self.winfo_pointery()

    def _apply_hover_to_default(self) -> None:
        x, y = self._current_hover_point()
        self.default_ball_position.set(f"{x},{y}")

    def _apply_hover_to_row(self, pos_var: tk.StringVar) -> None:
        x, y = self._current_hover_point()
        pos_var.set(f"{x},{y}")

    def _add_special_row(self, _parent: ttk.LabelFrame) -> None:
        name_var = tk.StringVar()
        pos_var = tk.StringVar(value="120,120")
        row = len(self.special_map_rows)

        ttk.Entry(self.mapping_rows_frame, textvariable=name_var).grid(row=row, column=0, sticky="ew", padx=(0, 8), pady=4)

        right = ttk.Frame(self.mapping_rows_frame)
        right.grid(row=row, column=1, sticky="ew", pady=4)
        right.columnconfigure(0, weight=1)

        ttk.Entry(right, textvariable=pos_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(right, text="Use Hover", command=lambda v=pos_var: self._apply_hover_to_row(v)).grid(
            row=0, column=1, padx=(6, 0)
        )

        self.special_map_rows.append({"name_var": name_var, "pos_var": pos_var})
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
        for row in self.special_map_rows:
            name_var = row["name_var"]
            pos_var = row["pos_var"]
            assert isinstance(name_var, tk.StringVar)
            assert isinstance(pos_var, tk.StringVar)

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
