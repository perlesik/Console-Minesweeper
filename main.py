from saper import *
import os
from time import sleep


while True:
    game = Saper()
    os.system("cls")

    # Starting configuration, setting field size, difficulty, bomb amount, flag amount and game state.
    game.startup()

    first_guess = True
    cleared_fields = []
    while game.game_state == "ongoing":
        os.system("cls")
        print(f"BOMB QUANTITY: {game.bomb_amount}")
        print(f"FLAGS USED: {game.bomb_amount - game.flags_amount}/{game.bomb_amount}")
        game.print_field()
        print()
        user_input = input("Type position: ").upper()
        if game.check_position(user_input):
            user_guess = game.convert_position(user_input)
            # First guess generates bombs, to prevent hitting bomb on first guess.
            if first_guess and "FLAG-" not in user_input and "F-" not in user_input:
                game.exclude_starting_cells(user_guess)
                game.generate_bombs()
                first_guess = False
            # Prevent guessing flagged fields.
            if game.field[user_guess[1]][user_guess[0]] == "P" and \
                    ("FLAG-" not in user_input or "F-" not in user_input):
                print("You can't guess flagged field.")
                sleep(1)
                continue
            if "FLAG-" in user_input or "F-" in user_input:
                # First check if it has been flagged. If true, un-flag the field.
                if game.field[user_guess[1]][user_guess[0]] == "P":
                    game.modify_cell(user_guess, "un-flag")
                    game.flags_pos.remove(user_guess)
                    game.flags_amount += 1
                elif game.field[user_guess[1]][user_guess[0]] == "■":
                    game.modify_cell(user_guess, "flag")
                    game.flags_pos.append(user_guess)
                    game.flags_amount -= 1
                else:
                    print("You can't put flag on empty field.")
                    sleep(1)
            # elif ":" in user_input:
            #     positions = get_positions_from_range(user_input)
            #     for single_pos in positions:
            #         # Skip flagged field.
            #         if field[single_pos[1]][single_pos[0]] == "P":
            #             continue
            #         if single_pos not in bombs_pos:
            #             modify_line(single_pos, "miss")
            #             if single_pos not in cleared_fields:
            #                 cleared_fields.append(single_pos)
            #         else:
            #             reveal_bombs()
            #             break
            elif user_guess not in game.bombs_pos:
                game.modify_cell(user_guess, "miss")
                empty_fields = game.get_blank_fields_nearby(user_guess)
                for field in empty_fields:
                    game.modify_cell(field, "miss")
                    if field not in cleared_fields:
                        cleared_fields.append(field)
                if user_guess not in cleared_fields:
                    cleared_fields.append(user_guess)
            # User guess equals bomb pos, player loses.
            else:
                game.reveal_bombs(user_guess)
                game.game_state = "lose"
            # Executes when player clears the field (flagging bombs is not necessary).
            if len(cleared_fields) == game.width * game.height - game.bomb_amount:
                game.game_state = "win"
        else:
            print("Wrong position.")
            sleep(1)

    os.system("cls")
    game.print_field()

    if game.game_state == "win":
        print("You have successfully cleared the field, you won!")
    else:
        print("You've hit the bomb, you lose..")

    new_game = ""
    while new_game not in ["y", "n"]:
        new_game = input("Do you want to start a new game? (y/n): ")
    if new_game == "n":
        print("Thanks for playing!")
        break
