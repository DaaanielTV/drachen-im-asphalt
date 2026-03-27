from src.game.renderer import GameRenderer
from src.game.session import GameSession


def main():
    renderer = GameRenderer()
    session = GameSession(renderer=renderer)

    renderer.render_start_menu()
    choice = input("Waehle eine Option (1-2): ")

    if choice == "1":
        protagonist, dragon = session.build_new_game()
    elif choice == "2":
        protagonist, dragon = session.build_loaded_game()
    else:
        print("Ungueltige Wahl! Neues Spiel wird gestartet.")
        hero_name = input("Gib den Namen deines Helden ein: ")
        from src.characters.protagonist import Protagonist
        from src.characters.dragon import ViceCityDragon

        protagonist = Protagonist(hero_name, "jason")
        protagonist.initialize_missions()
        dragon = ViceCityDragon()

    session.game_loop(protagonist, dragon)


if __name__ == "__main__":
    main()
