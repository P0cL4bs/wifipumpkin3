from cmd import Cmd
from core.utility.printer import *
from core.utility.collection import SettingsINI
import core.utility.constants as C
from os import popen
import sys

class ConsoleUI(Cmd):
    ''' shell console UI '''
    def __init__(self,parse_args=None):
        self.parse_args = parse_args
        Cmd.__init__(self)
        self.conf = SettingsINI(C.CONFIG_INI)
        self.set_prompt()
        self.setOptions()

    def setOptions(self):
        if (self.parse_args.pulp):
            self.loadPulpFiles(self.parse_args.pulp)
        elif (self.parse_args.xpulp):
            self.onecmd(self.parse_args.xpulp, ";")

    def set_prompt(self):
        self.prompt = '{} > '.format(setcolor('wp3',color='blue',underline=True))

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
        pass

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

    def default(self, args=str):
        for goodArgs in C.SYSTEMCOMMAND:
            if (args.startswith(goodArgs)):
                output = popen(args).read()
                if (len(output) > 0):
                    print(output) 


    def loadPulpFiles(self, file, data=None):
        ''' load and execute all commands in file pulp separate for \n '''
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
                f.close()
            if (data != None):
                self.onecmd(data, separator='\n')

    def onecmd(self, commands, separator=';'):
        ''' load command separate for ; file or string'''
        for command in commands.split(separator):
            Cmd.onecmd(self, command)

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




class ModuleUI(Cmd):
    ''' shell console UI '''
    _name_module = None
    completions = None
    options = None

    def __init__(self,parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        Cmd.__init__(self)
        self.conf = SettingsINI(C.CONFIG_INI)
        self.setOptions()

    def setOptions(self):
        if (self.parse_args.pulp):
            self.loadPulpFiles(self.parse_args.pulp)
        elif (self.parse_args.xpulp):
            self.onecmd(self.parse_args.xpulp, ";")

    def set_prompt_modules(self):
        self.prompt = 'wp3 : {} > '.format(setcolor(self.name_module,color='blue',underline=True))

    @property
    def name_module(self):
        return self._name_module

    @name_module.setter
    def name_module(self, name):
        self._name_module = name

    def do_back(self,args):
        """ go back one level"""
        try:    
            self.root["PumpkinShell"].getInstance().cmdloop('Starting prompt...')
        except IndexError as e:
            sys.exit(0)

    def do_set(self, args):
        ''' set options for module '''
        try:
            command,value = args.split()[0],args.split()[1]
            if (command in self.options.keys()):
                #self.conf.set('accesspoint',self.commands[command],value)
                print(display_messages('{} changed to => {}'.format(command, value),sucess=True))
                self.options.update({command: value})
            else:
                print(display_messages('unknown command: {} '.format(command),error=True))
                print(display_messages("Example : set host 127.0.0.1", info=True))
        except IndexError:
            pass

    def do_options(self, line):
        """ show options of current module"""
        print(display_messages('Available Options:',info=True,sublime=True))
        self.stdout.write('    {}	 {}\n'.format('Option', 'Value'))
        self.stdout.write('    {}	 {}\n'.format('------', '-----'))
        for option,value in self.options.items():
            self.stdout.write('    {:<10}	 {}\n'.format(option, value))
        print("\n")

    def do_help(self,args):
        """ show this help """
        names = self.get_names()
        cmds_doc = []
        names.sort()
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
            if (len(doc) > 0):
                self.stdout.write('    {:<10}	{}\n'.format(command, doc))
        print('\n')


    def loadPulpFiles(self, file, data=None):
        ''' load and execute all commands in file pulp separate for \n '''
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
                f.close()
            if (data != None):
                self.onecmd(data, separator='\n')

    def default(self, args=str):
        for goodArgs in C.SYSTEMCOMMAND:
            if (args.startswith(goodArgs)):
                output = popen(args).read()
                if (len(output) > 0):
                    print(output) 

    def complete_set(self, text, line, begidx, endidx):
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in self.completions if s.startswith(mline)]

    def emptyline(self):
        """ Do nothing on empty input line"""
        pass

    def onecmd(self, commands, separator=';'):
        ''' load command separate for ; file or string'''
        for command in commands.split(separator):
            Cmd.onecmd(self, command)

    def do_exit(self, args):
        sys.exit(0)
