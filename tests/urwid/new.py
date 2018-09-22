import urwid
import threading
import time
import logging
import socket
from multiprocessing import Process, Queue
from subprocess import (Popen, STDOUT, PIPE)

class Interface:
    palette = [
        ('body', 'white', 'black'),
        ('ext', 'white', 'dark blue'),
        ('ext_hi', 'light cyan', 'dark blue', 'bold'),
        ]

    header_text = [
        ('ext_hi', 'ESC'), ':quit        ',
        ('ext_hi', 'UP'), ',', ('ext_hi', 'DOWN'), ':scroll',
        ]

    def __init__(self):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'ext')
        self.flowWalker = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.flowWalker)
        self.footer = urwid.AttrWrap(urwid.Edit("Edit:  "), 'ext')
        self.view = urwid.Frame(
            urwid.AttrWrap(self.body, 'body'),
            header = self.header,
            footer = self.footer)
        self.loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input = self.unhandled_input)
        self.printer = Printer()

    def start(self):
        t1 = threading.Thread(target = self.fill_screen)
        t1.daemon = True
        t2 = threading.Thread(target = self.printer.fill_queue)
        t2.daemon = True
        t1.start()
        t2.start()
        self.loop.run()

    def unhandled_input(self, k):
        if k == 'esc':
            raise urwid.ExitMainLoop()
        if k == 'k':
            self.flowWalker.append(urwid.Text(('body', 'teste fim')))
            self.printer.started = False
            self.printer.procDHCP.terminate()
            self.printer.queue2.close()
            #self.loop.draw_screen()

    def fill_screen(self):
        while True:
            if self.printer.queue:
                self.flowWalker.append(urwid.Text(('body', self.printer.queue.pop(0))))
                try:
                    self.loop.draw_screen()
                    self.body.set_focus(len(self.flowWalker)-1, 'above')
                except AssertionError: pass

    def to_screen(self, text):
        self.queue.append(text)


class Printer:
    def __init__(self):
        self.message = 'Hello'
        self.queue = []
        self.cmd = ['ping','google.com']

    def standardProcOutput(self,q):
        with Popen(self.cmd, bufsize=1, stdout=PIPE,stderr=STDOUT, universal_newlines=True) as p:
            for line in p.stdout:
                q.put(line.encode())


    def fill_queue(self):
        # while 1:
        #     self.queue.append(self.message)
        #     time.sleep(2)
        self.queue2 = Queue()
        self.started = True
        self.procDHCP = Process(target=self.standardProcOutput, args=(self.queue2,))
        self.procDHCP.start()
        print('[New Thread {}]'.format(self.procDHCP.pid))
        while self.started:
            self.queue.append(self.queue2.get())


import cmd

class test_cli(cmd.Cmd):
    def __init__(self, intro="Demo of pyton cli",
        prompt="(tc)"):
        cmd.Cmd.__init__(self)
        self.intro=intro
        self.prompt=prompt
        self.doc_header="Test Cli (type help &lt;topic&gt;):"
        self.interface = Interface()

    def do_start(self, args):
        self.interface.start()

    def emptyline(self):
        pass
    def do_end(self, args):
        return True
    def help_end(self, args):
        print("End session")
    do_EOF = do_end
    help_EOF = help_end
    def do_quit(self, args):
        return True
    def help_quit(self, args):
        print("Quit session")
    def precmd(self, line):
        newline=line.strip()
        is_cmt=newline.startswith('#')
        if is_cmt:
            return ('')
        return (line)
    def do_nested(self, args):
        n_cli=test_level2_cli()
        n_cli.cmdloop()
    def help_nested(self, args):
        print("Start nested cli session")

class test_level2_cli(test_cli):
    def __init__(self):
        test_cli.__init__(self,
        intro="level 2 cli", prompt="(l2)")
    def do_print(self, args):
        print (args)
    def help_print(self):
        print (" Print the passed arguments ")

if __name__=='__main__':
   t_cli=test_cli()
   t_cli.cmdloop()