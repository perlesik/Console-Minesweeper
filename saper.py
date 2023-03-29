from random import choice, randint
import colorama

# TODO: 1. add timer, highscore in txt file, option to show highscores (add main menu)
# TODO: 2. in the main menu add settings to width, height and bombs, saved in settings.txt
# TODO: 3. add colors, make border out of letters/numbers lines (background color)
# TODO: flags - red font, bomb hit - red background, bomb indicators in default color, i.e. 1 - blue, 2 - green etc.
# TODO: 5. improve mine generation algorithm to exclude 50/50 situations
# TODO: 6. rework field functions


class Saper:
    def __init__(self):
        # Fields are 2-d lists.
        self.field = [[]]
        self.bomb_field = [[]]
        # Bomb percentages on standard levels.
        self.levels = {
            "easy": 10,
            "medium": 20,
            "hard": 30
        }
        # Size is defined by user, with 2x2 being the smallest and 26x99 the biggest [A-Z][1-99].
        self.height = 0
        self.width = 0
        self.bomb_amount = 0
        # Possible values are 'win', 'lose' and 'ongoing'.
        self.game_state = ""
        # Amount of flags placed on the field.
        self.flags_amount = 0
        # Positions of bombs in form of tuple coordinates
        self.bombs_pos = []
        # Positions of flags in form of tuple coordinates
        self.flags_pos = []
        # Cells excluded from bombs being generated on
        self.cells_excluded = []

    def startup(self):
        level = input("Pick level (easy/medium/hard/custom): ")
        self.set_field_size()
        self.add_columns()
        self.add_rows()
        self.set_bomb_amount(level)
        self.game_state = "ongoing"
        self.flags_amount = self.bomb_amount

    def print_field(self):
        """Prints game field with bombs hidden."""
        for row_num, row in enumerate(self.field):
            start = row[0]
            end = row[-1]
            middle = ""
            for i in range(1, self.height + 1):
                middle += f"{row[i]} "
            if row_num == 0 or row_num == len(self.field) - 1:
                line = f"{start}    "
                line += middle
                line += f"   {end}"
            else:
                line = f"{start}  "
                line += middle
                line += f" {end}"
            print(line)

    def add_columns(self):
        # field[0][0] and field[0][width + 1] contains ansi color formatting
        self.field[0].append(f"{colorama.Back.LIGHTWHITE_EX}{colorama.Fore.BLACK}")
        start_letter_value = 65  # Value of A in ASCII.
        for i in range(self.width):
            self.field[0].append(f"{chr(start_letter_value + i)}")
        self.field[0].append(f"{colorama.Style.RESET_ALL}")

    def add_rows(self):
        for i in range(1, self.height + 1):  # i is equal to game field row value
            self.field.append([])
            if self.height >= 10 > i:  # add leading blank space to rows 1-9 if there are 10 or more rows
                self.field[i].append(f" {i}")
            else:
                self.field[i].append(f"{i}")
            for _ in range(self.width):
                self.field[i].append("■")
            # add right side row numbers
            self.field[i].append(f"{i}")
        # Clone the header to the bottom row.
        self.field.append(self.field[0])

    def generate_bombs(self):
        letters = []
        for elem in self.field[0]:
            if len(elem) == 1 and 65 <= ord(elem) <= 90:
                letters.append(elem)
        bomb_list = []
        # -2 to skip the letters line that's on the bottom
        last_line = len(self.field) - 2
        i = 0
        while i < self.bomb_amount:
            letter = choice(letters)
            number = randint(1, last_line)
            position = self.convert_position(letter + str(number))
            if position not in bomb_list and position not in self.cells_excluded:
                self.bombs_pos.append(position)
                i += 1

    def exclude_starting_cells(self, pos):
        self.cells_excluded = self.get_nearby_fields(pos)

    def convert_position(self, pos):
        """Converts game position into tuple of indexes."""
        if "FLAG-" in pos:
            pos = pos.replace("FLAG-", "")
        elif "F-" in pos:
            pos = pos.replace("F-", "")
        column = ord(pos[0]) - 64  # Get ascii value and subtract 64, then A = 1, B = 2 etc.
        if self.height >= 10 and len(pos) == 3:  # If field height >= 10 it gets 2 digits from input;
            row = int(pos[1] + pos[2])      # otherwise 1 digit.
        else:
            row = int(pos[1])
        return column, row

    def check_position(self, pos):
        """Checks if entered position is valid, returns True or False."""
        letters = []
        for elem in self.field[0]:
            if len(elem) == 1 and 65 <= ord(elem) <= 90:
                letters.append(elem)
        # Check if flag command entered.
        if "FLAG-" in pos:
            new_pos = pos.replace("FLAG-", "")
            if self.check_position(new_pos):
                return True
            else:
                return False
        elif "F-" in pos:
            new_pos = pos.replace("F-", "")
            if self.check_position(new_pos):
                return True
            else:
                return False
        # Check for position range.
        # if ":" in pos:
        #     range_list = pos.split(":")
        #     range_start = range_list[0]
        #     range_end = range_list[1]
        #     if check_position(range_start) and check_position(range_end):
        #         if range_start[0] <= range_end[0] and range_start[1:] <= range_end[1:]:
        #             return True
        #         else:
        #             return False
        #     else:
        #         return False
        # Check if position is valid.
        if 2 > len(pos) > 3:
            return False
        # Check for letter on 2nd place (ascii characters not in <48, 57> range)
        if len(pos) == 2 and not 48 <= ord(pos[1]) <= 57:
            return False
        # Check for letter on 2nd and 3rd place (ascii characters not in <48, 57> range)
        if len(pos) == 3 and (not 48 <= ord(pos[1]) <= 57 or not 48 <= ord(pos[2]) <= 57):
            return False
        # Check for zero
        if int(pos[1]) == 0:
            return False
        # Check if width is too big.
        if pos[0] not in letters:
            return False
        # Check if height is too big.
        if len(pos) == 2:
            if int(pos[1]) > self.height:
                return False
        elif len(pos) == 3:
            if self.height < 10:
                return False
            num = int(pos[1] + pos[2])
            if num > self.height:
                return False
        else:
            return False
        return True

    def modify_cell(self, pos, status):
        """Exchanges cell in field with blank space, P, ■ or X depending on value of status."""
        col, row = pos[0], pos[1]
        if status == "miss":
            nearby_bombs_count = self.check_for_nearby_bombs(pos)
            if nearby_bombs_count:
                self.field[row][col] = f"{nearby_bombs_count}"
            else:
                self.field[row][col] = f" "
        elif status == "flag":
            self.field[row][col] = f"{colorama.Back.LIGHTBLACK_EX}P{colorama.Back.RESET}"
        elif status == "un-flag":
            self.field[row][col] = "■"
        elif status == "hit":
            self.field[row][col] = f"{colorama.Back.RED}X{colorama.Back.RESET}"
        elif status == "reveal":
            self.field[row][col] = "X"

    def get_blank_fields_nearby(self, pos):
        blank_cells = []
        cells_to_check = [pos]
        cells_checked = []

        def add_fields(position):
            if position in cells_checked:
                return
            nearby_fields = self.get_nearby_fields(position)
            for cell in nearby_fields:
                bomb_count = self.check_for_nearby_bombs(cell)
                if bomb_count == 0 and cell not in blank_cells:
                    blank_cells.append(cell)
                    if cell not in cells_to_check:
                        cells_to_check.append(cell)
                elif bomb_count > 0 and cell not in blank_cells:
                    blank_cells.append(cell)
        i = 0
        while len(cells_to_check) != len(cells_checked):
            # if there are bombs nearby guessed pos, it's not blank field
            if self.check_for_nearby_bombs(cells_to_check[0]) == 0:
                add_fields(cells_to_check[i])
                cells_checked.append(cells_to_check[i])
                i += 1
            else:
                return []
        return blank_cells

    def get_nearby_fields(self, pos):
        col, row = pos[0], pos[1]
        neighbour_cells = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 1 <= row + i <= self.height and 1 <= col + j <= self.width:
                    if self.field[row + i][col + j] == "■":
                        neighbour_cells.append((col + j, row + i))
        return neighbour_cells

    def check_for_nearby_bombs(self, pos):
        count = 0
        col, row = pos[0], pos[1]
        neighbour_cells = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbour_cells.append((col + j, row + i))
        for cell in neighbour_cells:
            if cell in self.bombs_pos:
                count += 1
        return count

    def set_field_size(self):
        self.width = int(input("Enter field width (max 26): "))
        self.height = int(input("Enter field height (max 99): "))
        if self.width > 26:
            self.width = 26
            print("Width has been set to 26, as it is max value.")
        elif self.width < 2:
            self.width = 2
            print("Width has been set to 2, as it is min value.")
        if self.height > 99:
            self.height = 99
            print("Height has been set to 99, as it is max value.")
        elif self.height < 2:
            self.height = 2
            print("Height has been set to 2, as it is min value.")

    def set_bomb_amount(self, lvl):
        field_size = self.height * self.width
        if lvl in self.levels:
            self.bomb_amount = int(field_size * self.levels[lvl] / 100)
        elif lvl == "custom":
            self.bomb_amount = int(input("Enter bomb amount: "))
            max_amount = int(self.height * self.width * 0.75)
            if self.bomb_amount > max_amount:
                self.bomb_amount = max_amount
                print(f"Bomb amount has been set to {max_amount}, as max 75% of field can be bombs.")
            elif self.bomb_amount < 1:
                self.bomb_amount = 1
                print(f"Bomb amount has been set to 1, as it is min value.")
        else:
            print("This level doesn't exists.")
            return

    def get_positions_from_range(self, range_str):
        position_list = []
        range_list = range_str.split(":")
        range_start = range_list[0]
        range_end = range_list[1]
        # Nested loop iterating over indexes from range_str, for example from A1 to C2, total of 6 iterations.
        for i in range(ord(range_start[0]), ord(range_end[0]) + 1):
            for j in range(int(range_start[1:]), int(range_end[1:]) + 1):
                position_list.append(self.convert_position(f"{chr(i)}{j}"))
        return position_list

    def reveal_bombs(self, pos):
        # Reveal all bombs locations.
        for bs in self.bombs_pos:
            if bs == pos:
                self.modify_cell(bs, "hit")
            else:
                self.modify_cell(bs, "reveal")
