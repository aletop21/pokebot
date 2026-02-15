import unittest

from bot_engine_auto import BallProfile, BattleBotEngine, BotConfig, CommandProfile, RecordingInputAdapter


class BattleBotEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = RecordingInputAdapter()
        config = BotConfig(
            command_profile=CommandProfile(name="default", commands=["m12", "m11"]),
            default_ball=BallProfile(name="Ultra", item_position=(100, 100)),
            ball_by_pokemon={"rhyperior": BallProfile(name="Heavy", item_position=(120, 120))},
        )
        self.engine = BattleBotEngine(config=config, input_adapter=self.adapter)

    def test_detects_new_pokemon_targets_second_and_sends_commands(self) -> None:
        self.engine.update_cycle(
            battle_entries=["Onix [55]", "Rhyperior [130]"],
            sprite_positions={"onix": (640, 370), "rhyperior": (670, 388)},
            battle_click_positions=[(900, 330), (900, 350)],
        )

        self.assertIn("click:left:900:350", self.adapter.events)
        self.assertIn("type:m12", self.adapter.events)
        self.assertIn("type:m11", self.adapter.events)

    def test_throws_ball_at_last_known_position_after_defeat(self) -> None:
        self.engine.update_cycle(
            battle_entries=["Onix [55]", "Rhyperior [130]"],
            sprite_positions={"onix": (640, 370), "rhyperior": (670, 388)},
            battle_click_positions=[(900, 330), (900, 350)],
        )
        self.adapter.events.clear()

        self.engine.update_cycle(
            battle_entries=["Onix [55]"],
            sprite_positions={"onix": (640, 370)},
            battle_click_positions=[(900, 330)],
        )

        self.assertEqual(self.adapter.events[0], "click:right:120:120")
        self.assertEqual(self.adapter.events[1], "click:right:670:388")


if __name__ == "__main__":
    unittest.main()
