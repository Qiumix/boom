import os
import colorama

key_binding = {
    "Up": ["j", "w"],
    "Down": ["k", "s"],
    "Left": ["h", "a"],
    "Right": ["l", "d"],
    "Other": ["q", "e"]
    #"q" -> flag
    #"e" -> reveal
}
BG = colorama.Back.GREEN
BB = colorama.Back.BLUE
BY = colorama.Back.YELLOW
RES = colorama.Style.RESET_ALL
Width = 3
board_line = 3
element = {"Boom": "*", "Unknow": "?", "Flag": "^", "Flat": " "}
num_key = [str(x) for x in range(10)]  ### 数字键
move = lambda line, col=1: cout(f"\033[{line};{col}H")
cout = lambda *printed: print(*printed, end="", sep="")
cline = lambda: (cout("\033[2K"))
cls = lambda: (cout("\033[2J\033[H"))
hide_cursor = lambda: cout("\033[?25l")
show_cursor = lambda: cout("\033[?25h")
up = lambda n: cout(f"\033[{n}A")
down = lambda n: cout(f"\033[{n}B")
right = lambda n: cout(f"\033[{Width * n}C")
left = lambda n: cout(f"\033[{Width * n}D")


### 利用 ANSI 转义序列实现清屏移动光标等
def init_program():
    """
    初始化程序
    """
    hide_cursor()
    try:
        os.system("")  #ANSI 转义序列支持
    except Exception:
        print("Failed to enable ANSI")
        exit()

    colorama.init()


def getch():
    """
    高阶函数封装判断平台过程
    """
    if os.name == "nt":
        from msvcrt import getch

        def win_get():
            return getch().decode()

        return win_get
    else:
        import termios
        from tty import setraw
        from sys import stdin

        def unix_get():
            fd = stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                setraw(stdin.fileno())
                ch = stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return unix_get


getch = getch()


def print_all(Line, All):
    """
    只在开始运行打印一次，后面通过光标移动更改
    """
    global board_line
    cls()
    move(board_line)
    cout("  +" + "-" * (Line * Width + Width - 1), "+\n")
    for i in All[1:]:
        cout("  | ")
        for j in i[1:]:
            cout(" ", j, " ")
        cout(" |\n")
    cout("  +" + "-" * (Line * Width + Width - 1), "+")


def print_line(cur_line, Line):
    t = cur_line


def move_info(line: int, col: int) -> int:
    global board_line
    return line + board_line, col * Width


def generate_boom(All: list, num: int) -> list:
    from random import randint
    Line = get_line(All)
    if num > Line**2 / 2:
        All[0][0] = False
        return All
    rand_line = (lambda Line: (lambda: randint(1, Line)))(Line)
    #高阶函数封装Line，配合lambda实现可读性极差(笑)
    t = num
    temp = set()
    while t > 0:
        pos = rand_line(), rand_line()
        if pos not in temp:
            temp.add(pos)
            t -= 1
    temp = list(temp)
    for i, j in temp:
        All[i][j] = element["Boom"]
    All[0] = True
    return All


def get_line(All):
    return len(All) - 1


def is_boom(pos, All):
    if All[pos[0]][pos[1]] == element["Boom"]:
        return True
    return False


def get_item(All, pos):
    return All[pos[0]][pos[1]]


def cal_count(Count, All):
    Line = get_line(All)
    for i in range(1, Line + 1):
        for j in range(1, Line + 1):
            all_edge = {(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                        (i + 1, j - 1), (i + 1, j), (i + 1, j + 1), (i, j - 1),
                        (i, j + 1)}

            positions = []
            for r, c in all_edge:
                if 1 <= r <= Line:
                    if r < len(All) and 1 <= c < len(All[r]):
                        positions.append((r, c))

            Count[i][j] = sum(1 for pos in positions if is_boom(pos, All))

    return Count


def show_line(line, Line):
    move(board_line + line)
    cout(BG, f"{abs(line):^2}", BB)
    for temp in range(1, Line + 1):
        if temp != line:
            move(board_line + temp, 1)
            relative = temp - line
            cout(f"{abs(relative):^2}")
        else:
            cout(BY)


def show_col(col, Line):
    _, term_col = move_info(1, col)

    move(board_line - 1, term_col + 1)
    cout(colorama.Back.GREEN, f"{col:^3}", BB)
    for temp_col in range(1, Line + 1):
        if temp_col != col:
            _, temp_term_col = move_info(1, temp_col)
            move(board_line - 1, temp_term_col + 1)
            relative = temp_col - col
            cout(f"{abs(relative):^3}")
        else:
            cout(BY)


def show_relevant(line, col, Line, All):
    show_line(line, Line)
    show_col(col, Line)
    shell_line, shell_col = move_info(line, col)
    move(shell_line, shell_col - 1)
    cout(BG, " ", All[line][col], " ", RES)


def click_item(line, col, Line, All, is_flaged, Count, is_revealed):
    if is_flaged[line][col] or is_revealed[line][col]:
        return False, All, is_flaged, is_revealed
    if All[line][col] == element["Boom"]:
        is_revealed[line][col] = True
        return True, All, is_flaged, is_revealed

    def inner(l, c):
        nonlocal All, is_flaged, is_revealed
        if l < 1 or l > Line or c < 1 or c > Line or is_revealed[l][c]:
            return

        if All[l][c] == element["Boom"]:
            return

        is_revealed[l][c] = True
        is_flaged[l][c] = False

        if Count[l][c] > 0:
            All[l][c] = str(Count[l][c])
            return
        else:
            All[l][c] = element["Flat"]
            for tl in [-1, 0, 1]:
                for tc in [-1, 0, 1]:
                    if tl == 0 and tc == 0:
                        continue
                    inner(l + tl, c + tc)

    inner(line, col)
    return False, All, is_flaged, is_revealed


def refresh_pos(pos, All, is_current=False):
    move(move_info(pos))
    left(1)
    if is_current:
        cout(BG)
    cout(" ", All[pos[0]][pos[1]], " ")
    if is_current:
        cout(RES)


def shell_move(direction, count=1):
    pass


def print_cursor(pos, All):
    move(move_info(*pos))
    left


def clear_bg(icon, pre_pos):
    shell_line, shell_col = move_info(pre_pos[0], pre_pos[1])
    move(shell_line, shell_col - 1)
    cout(BG, " ", icon, " ", RES)


def print_message(Line, message, pre_pos, error=False):
    move(board_line + Line + (5 if error else 6))
    cline()
    cout(message)
    move(*pre_pos)


def clear_error(Line, pre_pos):
    move(board_line + Line + 6)
    cline()
    move(*pre_pos)


def get_key(Line, cursor_pos):
    current_key = None
    num_buffer = []
    is_ok = False
    while not is_ok:
        try:
            clear_error(Line, cursor_pos)
            if num_buffer:
                print_message(Line, str(num_buffer), cursor_pos)
            current_key = getch()
            if current_key in num_key:
                num_buffer.append(current_key)
            elif not any(current_key in keys for keys in key_binding.values()):
                print_message(Line, f"key {current_key} is invalid!",
                              cursor_pos, True)
            else:
                is_ok = True
        except Exception as e:
            print_message(Line, f"Error: {str(e)}", cursor_pos, True)
    return num_buffer, current_key


def run(Line=10, All=None):
    init_program()

    if not All:
        All = [[False]] + [[element["Unknow"] for _ in range(Line + 1)]
                           for _ in range(Line)]
    else:
        Line = get_line(All)

    is_flaged = [[False] * (Line + 1) for _ in range(Line + 1)]
    is_revealed = [[False] * (Line + 1) for _ in range(Line + 1)]
    Count = [[0 for _ in range(Line + 1)] for _ in range(Line + 1)]
    print_all(Line, All)
    cursor_pos = (Line // 2 if Line > 1 else 1, Line // 2 if Line > 1 else 1)
    show_relevant(*cursor_pos, Line, All)

    All = generate_boom(All, Line * 2)
    Count = cal_count(Count, All)
    # main loop
    while True:
        number_buffer, current_key = get_key(Line, cursor_pos)
        if current_key in key_binding["Other"]:
            print_message(Line, "", cursor_pos)
            if current_key == key_binding["Other"][0]:
                is_flaged[cursor_pos[0]][cursor_pos[1]] = True
            else:
                is_revealed[cursor_pos[0]][cursor_pos[1]] = True
        else:
            for direction, keys in key_binding.items():
                if current_key in keys:
                    motion = direction
                    break
            clear_bg(get_item(All, cursor_pos), cursor_pos)

    #

    show_cursor()
    move(1)
    down(Line + board_line + 3)


def start():
    pass


run()
