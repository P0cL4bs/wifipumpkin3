import logging, queue, sys, threading, time

import urwid

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)-4s %(threadName)s %(message)s",
    datefmt="%H:%M:%S",
    filename='trace.log',
)

class Interface:
    palette = [
        ('body', 'white', ''),
        ('ext', 'white', 'dark blue'),
        ('ext_hi', 'light cyan', 'dark blue', 'bold'),
        ]

    header_text = [
        ('ext_hi', 'ESC'), ':quit        ',
        ('ext_hi', 'UP'), ',', ('ext_hi', 'DOWN'), ':scroll',
        ]

    def __init__(self, msg_queue):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'ext')
        self.flowWalker = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.flowWalker)
        self.flowWalker2 = urwid.SimpleListWalker([])
        self.body2 = urwid.ListBox(self.flowWalker2)
        self.footer = urwid.AttrWrap(urwid.Edit("Edit:  "), 'ext')
        self.view = urwid.Frame(
            urwid.AttrWrap(self.body, 'body'),
            header = self.header,
            footer = self.footer)
        blank = urwid.Divider()
        self.main_box = urwid.LineBox(self.body)
        self.main_box2 = urwid.LineBox(self.body2)
        self.columns = urwid.Columns([self.main_box], dividechars=1)
        self.columns2 = urwid.Columns([self.main_box2], dividechars=1)
        self.main_layout = urwid.Pile([
            self.columns,
            self.columns2,
        ])
        self.view = urwid.Frame(
            urwid.AttrWrap(self.main_layout, 'body'),
            header = self.header,
            footer = self.footer)
        self.loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input = self.unhandled_input)
        self.msg_queue = msg_queue
        self.check_messages(self.loop, None)

    def unhandled_input(self, k):
        if k == 'esc':
            raise urwid.ExitMainLoop()

    def check_messages(self, loop, *_args):
        """add message to bottom of screen"""
        loop.set_alarm_in(
            sec=0.5,
            callback=self.check_messages,
            )
        try:
            msg = self.msg_queue.get_nowait()
        except :
            return
        self.flowWalker.append(
            urwid.Text(('body', msg))
            )
        self.body.set_focus(
            len(self.flowWalker)-1, 'above'
            )

def update_time(stop_event, msg_queue):
    """send timestamp to queue every second"""
    logging.info('start')
    while not stop_event.wait(timeout=1.0):
        msg_queue.put( time.strftime('time %X') )
    logging.info('stop')

if __name__ == '__main__':

    stop_ev = threading.Event()
    message_q = queue.Queue()

    threading.Thread(
        target=update_time, args=[stop_ev, message_q],
        name='update_time',
    ).start()

    logging.info('start')
    Interface(message_q).loop.run()
    logging.info('stop')

    # after interface exits, signal threads to exit, wait for them
    logging.info('stopping threads')

    stop_ev.set()
    for th in threading.enumerate():
        if th != threading.current_thread():
            th.join()