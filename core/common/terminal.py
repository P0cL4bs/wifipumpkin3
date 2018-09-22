from cmd import Cmd
from core.utility.printer import *
from core.utility.collection import SettingsINI
import core.utility.constants as C

class ConsoleUI(Cmd):
    ''' shell console UI '''
    def __init__(self,options=None):
        Cmd.__init__(self)
        self.conf = SettingsINI(C.CONFIG_INI)
        self.set_prompt()

    def set_prompt(self):
        self.prompt = '{} > '.format(setcolor('wp-ng',color='blue',underline=True))

    def do_modules(self,args):
        """ show modules available"""
        pass
    def do_search(self,args):
        """ search  modules by name"""
        pass

    def do_use(self,args):
        """ load module on session"""
        pass

    def do_back(self,args):
        """ unload module on session"""
        self.session['ModuleHandler'] = ''
        self.session['Commands'] = []
        self.updatePrompt()

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        Cmd.preloop(self)   ## sets up command completion
        self._hist    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}


    def do_help(self,args):
        """ show this help """
        names = self.get_names()
        cmds_doc = []
        names.sort()
        exeptionsCommands = ['sessions','listener','help','exit','modules',
        'use','search','back','set','unset','info','run']
        print(display_messages('Available Commands:',info=True,sublime=True))
        for name in names:
            if name[:3] == 'do_':
                pname = name
                cmd   = name[3:]
                if getattr(self, name).__doc__:
                    cmds_doc.append((cmd, getattr(self, name).__doc__))
                else:
                    cmds_doc.append((cmd, ""))

        #self.stdout.write('%s\n'%str(self.doc_header))
        self.stdout.write('    {}	 {}\n'.format('Commands', 'Description'))
        self.stdout.write('    {}	 {}\n'.format('--------', '-----------'))
        for command,doc in cmds_doc:
            self.stdout.write('    {:<10}	{}\n'.format(command, doc))
        print('\n')

    def default(self, args):
        pass

    def precmd(self, line):
        newline=line.strip()
        is_cmt=newline.startswith('#')
        if is_cmt:
            return ('')
        return (line)

    def postcmd(self, stop, line):
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_exit(self, args):
        """ exit the program."""
        print('Quitting.')
        raise SystemExit