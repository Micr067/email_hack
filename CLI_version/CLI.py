# -*- coding: utf-8 -*-

import EmailBomb
import threading
import curses
import time
import locale
locale.setlocale(locale.LC_ALL, '')


class Screen:
    UP = -1
    DOWN = 1

    LEFT = -1
    RIGHT = 1

    COLORS = {
        "red": 1,
        "yellow": 2,
        "cyan": 3,
        "green": 4,
        "white": 5,
        "gray": 6,
    }

    def __init__(self):
        self.too_small = False

        self.init_curses()

        self.top = 0
        self.bottom = len(CLIENTS)+1
        self.max_lines = curses.LINES-len(LOGO)

        self.hori_len = 0
        self.EXIT_FLAG = 0

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr()
        self.height, self.width = self.window.getmaxyx()
        if self.width < 60:
            self.too_small = True
            return

        self.window.keypad(True)
        # self.window.nodelay(True)

        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_CYAN)

    def put_color(self, color, bold=True):
        bold = [bold, curses.A_BOLD][bold]

        return {
            "red": curses.color_pair(1),
            "yellow": curses.color_pair(2),
            "white": curses.color_pair(3),
            "green": curses.color_pair(4),
        }[color] | bold

    def input_stream(self):
        """Waiting an input and run a proper method according to type of input"""

        while any([client.running for client in CLIENTS]):
            ch = self.window.getch()

            if ch == curses.KEY_UP:
                self.scroll(self.UP)

            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)

            elif ch == curses.KEY_LEFT:
                self.scroll(self.LEFT, horizontal=True)

            elif ch == curses.KEY_RIGHT:
                self.scroll(self.RIGHT, horizontal=True)

            elif ch == ord("q"):
                self.EXIT_FLAG = 1

    def display(self):
        """Display the CLIENTS on window"""
        condition = 1
        while condition:
            try:
                self.window.erase()
                if self.EXIT_FLAG:
                    condition = any([client.running for client in CLIENTS])
                    for client in CLIENTS:
                        if not client.exit_flag:
                            client.exit_flag = self.EXIT_FLAG
                        else:
                            if client.running:
                                client.status = [(client.status_header, "exiting", "yellow")]
                            else:
                                client.status = [(client.status_header, "exited", "red")]

                for idx, item in enumerate(LOGO+CLIENTS[self.top:self.top + self.max_lines-1]):
                    data = item.status[0] if len(item.status) == 1 else item.status.pop()

                    len_data = len(data[0]+data[1])
                    tmp_height, tmp_width = self.window.getmaxyx()

                    # ??????????????????????????? win ?????????????????? resize
                    if self.width < len_data:
                        self.width = len_data
                        self.window.resize(self.height, self.width)
                        time.sleep(1)

                    # ?????????????????????????????? resize
                    if tmp_width != self.width:
                        self.width = max(self.width, tmp_width)
                        self.window.resize(self.height, self.width)
                        time.sleep(1)

                    # ?????????????????????????????? resize
                    if tmp_height != self.height:
                        self.max_lines = min(self.height, tmp_height)
                        self.height = max(self.height, tmp_height)
                        self.window.resize(self.height, self.width)
                        self.top = 0
                        time.sleep(1)

                    try:
                        self.window.addstr(idx, 0, data[0], self.put_color("white"))
                        tmp_length = len(data[0])
                        self.window.addstr(idx, tmp_length, data[1][self.hori_len:], self.put_color(data[2]))
                    except Exception:
                        self.EXIT_FLAG = 1
                        break
                        # self.window.addstr(idx, 0, "too small", self.put_color("white"))

                self.window.addstr(
                    idx+1,
                    0,
                    "status: "+["running", "exiting"][self.EXIT_FLAG]+" "*2,
                    curses.color_pair(5) | curses.A_BOLD
                )

                success_num = 0
                failed_num = 0.0001
                for client in CLIENTS:
                    failed_num += client.failed_num
                    success_num += client.success_num

                self.window.addstr(
                    idx+1,
                    17,
                    "success: "+"{}%".format(round(success_num/(success_num+failed_num)*100, 2)),
                    curses.color_pair(5) | curses.A_BOLD
                )

                self.window.refresh()

                # time.sleep(0.5)

            except KeyboardInterrupt:
                self.EXIT_FLAG = 1

    def scroll(self, direction, horizontal=False):
        '''
        ???????????????????????????
        '''

        if horizontal:  # ????????????
            if (
                # self.hori_len > 0?????????????????????????????????????????????
                direction == self.LEFT and self.hori_len > 0
            ) or (
                # ???????????????
                direction == self.RIGHT
            ):
                self.hori_len += direction

        else:  # ????????????
            if (
                direction == self.UP and self.top > 0
            ) or (
                direction == self.DOWN and self.top + self.max_lines < self.bottom
            ):
                self.top += direction

    def run(self):
        """Continue running the TUI until get interrupted"""

        self.display()

        # ?????? iTerm2
        # os.system("printf '\e]50;ClearScrollback\a'")
        # ???????????? :D

        curses.endwin()

        # screen ????????????????????????
        # ?????? process_data ??????


class LOGOLine:
    def __init__(self, data):
        self.status = [(data, "", "red")]


# ---------- ???????????? -----------


LOGO = [
    LOGOLine(i) for i in [
        "",
        "????????????????????????     ?????????  ?????????",
        "????????????????????????     ?????????  ?????????",
        "??????????????????       ????????????????????????",
        "??????????????????       ????????????????????????",
        "????????????????????????     ?????????  ?????????",
        "????????????????????????mail ?????????  ?????????acker",
        "",
    ]
]

THREADS_NUM = 30

CLIENTS = [
    EmailBomb.EmailBomb(
        id=id,
        from_addr="hr@361.com",
        to_addr="@163.com",
    ) for id in range(THREADS_NUM)
]  # ???????????? client
# ------------------------------
sc = Screen()  # ?????? CLI ????????????


if sc.too_small:
    print("too small")
else:
    for client in CLIENTS:
        thread = threading.Thread(target=client.attack, args=("hello! my friend!", "hr: you got it!",))
        thread.setDaemon(True)
        thread.start()  # ???????????? client

    t = threading.Thread(target=sc.input_stream)
    t.setDaemon(True)
    t.start()

    sc.run()
