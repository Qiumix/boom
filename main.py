import os
import colorama
import time
import signal
import threading
import json
# 一些常量
key_binding = {
    "Up": ["k", "w", "^"],
    "Down": ["j", "s", "v"],
    "Left": ["h", "a", "<"],
    "Right": ["l", "d", ">"],
    "Other": ["f", "e", "q", "bs"]
    # "f" --> flag
    # "e" --> reveal
    # "q" --> quit
    # "bs" --> backspace
}
all_key = []
for values in key_binding.values():
    all_key.extend(values)
load_icon = (("◜", "◠", "◝", "◞", "◡", "◟"), ("◰", "◳", "◲", "◱"),
             ("( ●    )", "(  ●   )", "(   ●  )", "(    ● )", "(     ●)",
              "(    ● )", "(   ●  )", "(  ●   )", "( ●    )", "(●     )"))
BG = colorama.Back.GREEN
BB = colorama.Back.BLUE
BW = colorama.Back.WHITE
BY = colorama.Back.YELLOW
FB = colorama.Fore.BLACK
FW = colorama.Fore.WHITE
RES = colorama.Style.RESET_ALL
Width = 3
board_line = 3
element = {"Boom": "*", "Unknow": "?", "Flag": "^", "Flat": " "}
num_key = [str(x) for x in range(10)]  ### 数字键

move = lambda line, col=1: cout(f"\033[{line};{col}H")  # 绝对移动
cout = lambda *printed: print(*printed, end="", sep="")  # 改变默认参数的print
cline = lambda: (cout("\033[2K"))  # 清行
cls = lambda: (cout("\033[2J\033[H"))  # 清屏
hide_cursor = lambda: cout("\033[?25l")
show_cursor = lambda: cout("\033[?25h")
# 下面四个(相对坐标移动)好像都没用到，用的绝对坐标
up = lambda n: cout(f"\033[{n}A")
down = lambda n: cout(f"\033[{n}B")
right = lambda n: cout(f"\033[{n}C")
left = lambda n: cout(f"\033[{n}D")
# 判断当前shell(os.system用到的命令区别, bash touch, cmd/pwsh ni, etc)
shell_env = os.environ.get('SHELL')
if shell_env is None:  # Windows systems often don't have SHELL environment variable
    shell_mode = 1
else:
    shell = shell_env.decode().strip().split() if isinstance(
        shell_env, bytes) else shell_env.strip().split()
    if "powershell" in shell or "cmd" in shell:
        shell_mode = 1
    else:
        shell_mode = 0
#### ai 改了下windows shell环境判定(linux可以直接用原来的, win就有问题)


### 利用 ANSI 转义序列实现清屏移动光标等
def init_program():
    """
    初始化程序
    """
    hide_cursor()
    colorama.init(autoreset=True)


def exiting(Line, pt: threading.Thread):
    move(1)
    down(Line + board_line + 6)
    show_cursor()
    if pt:
        setattr(pt, "stop", True)
        pt.join(0)
    exit(0)


# getch实现无缓冲输入(win是c/c++同款，直接调用msvcrt动态链接库，类unix是ai写的, 看不懂)
def make_getch():
    """
    高阶函数封装判断平台过程
    """
    if os.name == "nt":
        """
        Windows NT内核，其余基本都是类unix(posix, 是一个标准而不是内核名称)，除了ChromeOS之类的怪胎
        类unix包括unix, linux, 各种BSD之类的内核
        pthon3的os库里name的判定只有nt和posix两种, python2有mac之类的, mac也是基于unix
        sys.platform可以判定具体平台,
        因为只有win一个独狼不支持termios库和posix里的的一些东西，这里直接用os.name
        msvctr的getch性能应该更好? 毕竟直接调用visual c++(这玩意好像没开源, 其他系统没有)
        """
        from msvcrt import getch

        def win_get() -> str:
            temp_c = getch()  # decode解码将byte对象转字符串

            if temp_c == b'\x08':  # 退格键
                return "bs"

            # 处理方向键（两字节）
            if temp_c in (b'\xe0', b'\x00'):
                temp_c = getch()
                # win方向键映射表
                direction_key = {
                    b'H': '^',  # 上
                    b'P': 'v',  # 下
                    b'K': '<',  # 左
                    b'M': '>'  # 右
                }
                return direction_key.get(temp_c, temp_c)

            return temp_c.decode()

        return win_get
    else:
        import sys
        import termios
        import tty

        def getch_unix():
            # 做完了google了一下发现可以pip install getch，不过懒得搞了，还得弄方向键映射
            # debian系强制apt装python库挺难受的，apt里没有getch
            # windows的话装getch包会构建错误，不知道为啥，缺依赖项？
            # 解决了，需要14.0以上的msvc，没装visual studio所以放弃了，直接用msvcrt不好嘛
            """优化后的Unix getch实现"""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)

                # 读取第一个字符
                first_char = sys.stdin.read(1)

                # 处理方向键（以ESC开头）
                if first_char == '\x1b':
                    # 读取后续字符
                    second_char = sys.stdin.read(1)
                    if second_char == '[':
                        third_char = sys.stdin.read(1)
                        return {
                            'A': '^',  # 上
                            'B': 'v',  # 下
                            'C': '>',  # 右
                            'D': '<'  # 左
                        }.get(third_char, '')
                    # 其他ESC序列直接返回原始字符
                    return first_char + second_char

                # 处理退格键
                elif first_char in ('\x7f', '\x08'):  # DEL 和 Backspace
                    return 'bs'

                # 普通字符
                else:
                    return first_char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return getch_unix
    import getch as _getch


getch = make_getch()


def print_all(Line, All):
    """
    只在开始运行打印一次，后面通过光标移动更改
    """
    cls()
    move(board_line)
    cout(f"  {BW}   " + " " * (Line * Width + Width), f"\n\r")
    for i in All[1:]:
        cout(f"  {BW}   ")
        for j in i[1:]:
            cout(" ", j, " ")
        cout(f"{BW}   \n\r")
    cout(f"  {BW}   " + " " * (Line * Width + Width), f"\n\r")


def move_info(line: int, col: int) -> tuple:
    # ":*"和"->*"都是类型注释
    """
    将行列号转终端光标坐标
    """
    global board_line
    return line + board_line, col * Width + 4


def generate_boom(All: list, num: int) -> list:
    """
    生成炸弹
    """
    Origin = [i[:] for i in All]
    from random import randint
    Line = get_line(Origin)

    rand_line = (lambda Line: (lambda: randint(1, Line)))(Line)
    # 高阶函数封装参数Line，配合lambda定义调用放一起实现可读性极差(笑)
    temp = set()
    while num > 0:
        pos = rand_line(), rand_line()
        if pos not in temp:
            temp.add(pos)
            num -= 1
    for i, j in list(temp):
        Origin[i][j] = element["Boom"]
    Origin[0] = True  # 用来标记是否成功生成炸弹
    return Origin


def get_line(item_set):
    """
    获取棋盘的边长
    """
    return len(item_set) - 1


def is_boom(pos, Origin):
    if Origin[pos[0]][pos[1]] == element["Boom"]:
        return True
    return False


def get_item(item_set, pos):
    """
    获得对应元素
    """
    return item_set[pos[0]][pos[1]]


def cal_count(Count, Origin):
    """
    计算每个位置炸弹数量
    """
    Line = get_line(Origin)
    for i in range(1, Line + 1):
        for j in range(1, Line + 1):
            all_edge = {(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                        (i + 1, j - 1), (i + 1, j), (i + 1, j + 1), (i, j - 1),
                        (i, j + 1)}
            positions = [(r, c) for r, c in all_edge
                         if 1 <= r <= Line and 1 <= c <= Line]
            Count[i][j] = sum(1 for pos in positions if is_boom(pos, Origin))

    return Count


def show_line(line, Line):
    """
    显示相对行号
    """
    move(board_line + line)
    cout(BG + FB + f"{line:^2}")
    for temp_line in range(1, Line + 1):
        if temp_line != line:
            move(board_line + temp_line, 1)
            relative = temp_line - line
            cout((BB + FW if temp_line < line else BY + FB) +
                 f"{abs(relative):^2}")
        else:
            pass


def show_col(col, Line):
    """
    相对列号
    """
    _, term_col = move_info(1, col)  # 用不到的变量用下划线

    move(board_line - 1, term_col - 1)
    cout(BG + FB + f"{col:^3}")
    for temp_col in range(1, Line + 1):
        if temp_col != col:
            _, term_col = move_info(1, temp_col)
            move(board_line - 1, term_col - 1)
            relative = temp_col - col
            cout((BB + FW if temp_col < col else BY + FB) +
                 f"{abs(relative):^3}")
        else:
            pass


def show_relevant(line, col, Line, All):
    """
    显示相对行列号，高亮当前元素
    """
    show_line(line, Line)
    show_col(col, Line)
    shell_line, shell_col = move_info(line, col)
    move(shell_line, shell_col - 1)
    cout(BG + FB + " " + get_item(All, (line, col)) + " ")


def click_item(line, col, Line, All, Origin, is_flaged, Count, is_revealed):
    """
    实现reveal动作, (click指原版扫雷点鼠标, 这里实际是摁键盘)
    """
    if is_flaged[line][col] or is_revealed[line][col]:
        return False, All, is_flaged, is_revealed
    if Origin[line][col] == element["Boom"]:
        is_revealed[line][col] = True
        return True, All, is_flaged, is_revealed

    def inner(l, c):
        """
        递归大法好，翻牌子
        """
        nonlocal All, is_flaged, is_revealed
        # nonlocal关键字调用父帧变量
        # 不加也可以调用，但是如果进行赋值操作会变成局部变量，不会影响父帧中同变量
        # global同理，不过调用的是全局帧的变量
        if l < 1 or l > Line or c < 1 or c > Line or is_revealed[l][c]:
            # 越界或者已经判定过直接pass
            return

        if Origin[l][c] == element["Boom"]:
            # 炸弹pass
            return

        is_revealed[l][c] = True
        is_flaged[l][c] = False

        if Count[l][c] > 0:
            All[l][c] = str(Count[l][c])
            return
        else:  # 递归主体，其他为base case(基例/基线)
            All[l][c] = element["Flat"]
            for tl in [-1, 0, 1]:
                for tc in [-1, 0, 1]:
                    if tl == 0 and tc == 0:
                        continue
                    inner(l + tl, c + tc)

    inner(line, col)
    print_all(Line, All)
    return False, All, is_flaged, is_revealed


def clear_bg(icon, pre_pos):
    """
    规则为当前光标所在格子高亮
    这个函数的作用是清除高亮效果(重打印嘛)
    高亮的部分放在show_relvant里了
    """
    term_line, term_col = move_info(pre_pos[0], pre_pos[1])
    move(term_line, term_col - 1)
    cout(" ", icon, " ", RES)


def print_message(Line, message, pre_pos, error=False):
    """
    打印信息，包括报错和按键
    """
    move(board_line + Line + (3 if error else 4))
    cline()
    cout(message)
    move(*pre_pos)


def get_key(Line, cursor_pos, pt):
    """
    获取按键和数字键
    """
    current_key = None
    num_buffer = 0
    is_ok = False
    while not is_ok:
        try:
            current_key = getch()
            print_message(Line, "", cursor_pos)  # 清除消息的，调用里面的cline
            print_message(Line, "", cursor_pos, True)
            if current_key in num_key:
                num_buffer = num_buffer * 10 + int(current_key)
            elif current_key in all_key:
                if current_key == key_binding["Other"][2]:
                    exiting(Line, pt)
                elif current_key == key_binding["Other"][3]:
                    num_buffer //= 10
                else:
                    is_ok = True
            else:
                print_message(Line, f"Invalid key: '{current_key}'",
                              cursor_pos, True)
            print_message(
                Line, " " * (Line * Width // 2 + Width) +
                (str(num_buffer) if num_buffer else "") +
                ("" if current_key == key_binding["Other"][3]
                 or current_key in num_key else current_key), cursor_pos)
        except Exception as e:
            print_message(Line, f"Error: {str(e)}", cursor_pos, True)
            exit(0)
    return max(num_buffer, 1), current_key


def move_cursor_info(motion, cursor_pos, total, Line):
    """
    返回移动后的坐标，用max和min简化了，之前的又臭又长
    """
    if motion == "Up":
        return [max(1, cursor_pos[0] - total), cursor_pos[1]]
    elif motion == "Down":
        return [min(Line, cursor_pos[0] + total), cursor_pos[1]]
    elif motion == "Left":
        return [cursor_pos[0], max(1, cursor_pos[1] - total)]
    elif motion == "Right":
        return [cursor_pos[0], min(Line, cursor_pos[1] + total)]


def print_boom(pos):
    """
    Boom 的时候红色高亮炸弹
    """
    move(*move_info(*pos))
    left(1)
    cout(colorama.Back.RED + FB + " " + element["Boom"] + " ")


def count_remain(All, boom_count):
    """
    判定是否win game用的
    """
    total = get_line(All)**2
    count = 0
    for i in All[1:]:
        for j in i[1:]:
            if j == element["Flat"] or j in num_key:
                count += 1
    return (total - count) == boom_count


def run(Line=10,
        boom_count=None,
        pt=None,
        All=None,
        Origin=None,
        is_flaged=None,
        is_revealed=None,
        total_time=0):
    init_program()

    #判断是否给定数据，并生成缺失数据
    if not boom_count:
        boom_count = Line
    boom_count = min(boom_count, Line**2 // 4)  # 限制下炸弹数量
    if not Origin:
        All = [[False]] + [[element["Unknow"] for __ in range(Line + 1)]
                           for _ in range(Line)]
        Origin = generate_boom(All, boom_count)
    else:
        Line = get_line(All)
    if not is_flaged:
        is_flaged = [[False] * (Line + 1) for _ in range(Line + 1)]
    if not is_revealed:
        is_revealed = [[False] * (Line + 1) for _ in range(Line + 1)]
    Count = [[0 for _ in range(Line + 1)] for _ in range(Line + 1)]

    #######################

    print_all(Line, All)
    pos = [Line // 2 if Line > 1 else 1, Line // 2 if Line > 1 else 1]
    show_relevant(*pos, Line, All)

    Count = cal_count(Count, Origin)

    # mainloop --> 又臭又长 #

    start = time.time()
    while True:
        total, current_key = get_key(Line, pos, pt)

        if current_key in key_binding["Other"]:  # flag or reveal

            print_message(Line, "", pos)  # 清除信息，flag与reveal行为不能与数字组合
            if current_key == key_binding["Other"][0]:
                is_flaged[pos[0]][pos[1]] = not get_item(is_flaged, pos)
                if get_item(is_flaged, pos):
                    if get_item(All, pos) == element["Unknow"]:
                        All[pos[0]][pos[1]] = element["Flag"]
                elif get_item(All, pos) == element["Flag"]:
                    All[pos[0]][pos[1]] = element["Unknow"]
                show_relevant(*pos, Line, All)

            else:

                is_boomed, All, is_flaged, is_revealed = click_item(
                    *pos, Line, All, Origin, is_flaged, Count, is_revealed)
                ##########
                if is_boomed:
                    print_boom(pos)
                    take_time = time.time() - start
                    print_message(Line, f"BOOM! Time:{take_time:.2f}", pos)
                    from playsound import playsound
                    # playsound("boom.mp3")
                    exiting(Line, pt)
                if count_remain(All, boom_count):
                    take_time = time.time() - start
                    print_message(Line, f"WIN! Time:{take_time:.2f}", pos)
                    exiting(Line, pt)
                ##########
                show_relevant(*pos, Line, All)
        else:  # move cursocr
            for direction, keys in key_binding.items():
                if current_key in keys:
                    motion = direction
                    break
            clear_bg(get_item(All, pos), pos)
            pos = move_cursor_info(motion, pos, total, Line)
            show_relevant(*pos, Line, All)

    #


#############################
def start(judge=False):

    def print_time_icon():
        count = 0
        Len = len(load_icon[2])
        running = True
        while running:
            move(1)
            cout(load_icon[2][count % Len], "   ", count / 10)
            count += 1
            time.sleep(0.1)
            if getattr(threading.current_thread(), "stop", False):
                break

    pt = threading.Thread(target=print_time_icon)
    if judge:
        pt.start()
    else:
        pt = None
    Line = 10
    boom_count = 10

    def signal_handler():
        """
        劫持信号
        """
        exiting(Line)

    if os.name == "nt":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        signal.signal(signal.SIGTSTP, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
    run(Line, boom_count, pt=pt)


start()
#############################

# Line = 10
# All = [[False]] + [[element["Unknow"] for _ in range(Line + 1)]
#                    for _ in range(Line)]
