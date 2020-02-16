
colors = {'BOLD': '\033[1m','BLUE': '\033[34m' ,
            'GREEN': '\033[32m','YELLOW' :'\033[33m',
            'RED': '\033[91m','ENDC' : '\033[0m','CIANO' :'\033[1;36m','ORAN' : '\033[91m',
            'GREY': '\033[37m','DARKGREY' : '\033[1;30m','UNDERLINE' : '\033[4m'}

def banner(name=''):
    print ('''
 _ _ _  _  ___  _       ___                   _    _      
| | | |<_>| __><_> ___ | . \ _ _ ._ _ _  ___ | |__<_>._ _
| | | || || _> | ||___||  _/| | || ' ' || . \| / /| || ' |
|__/_/ |_||_|  |_|     |_|  `___||_|_|_||  _/|_\_\|_||_|_|
                                        |_|  
                                        
                                            codename: {}'''.format(name))

def setcolor(text,color='',underline=False):
    strcolored = {
        'blue':'{}{}{}{}'.format(colors['BOLD'],colors['BLUE'],text,colors['ENDC']),
        'red': '{}{}{}{}'.format(colors['BOLD'], colors['RED'], text, colors['ENDC']),
        'ciano': '{}{}{}{}'.format(colors['BOLD'], colors['CIANO'], text, colors['ENDC']),
        'green': '{}{}{}{}'.format(colors['BOLD'], colors['GREEN'], text, colors['ENDC']),
        'yellow': '{}{}{}{}'.format(colors['BOLD'], colors['YELLOW'], text, colors['ENDC']),
        'grey': '{}{}{}{}'.format(colors['BOLD'], colors['GREY'], text, colors['ENDC']),
        'darkgrey': '{}{}{}{}'.format(colors['BOLD'], colors['DARKGREY'], text, colors['ENDC'])
        }
    if underline:
        return colors['UNDERLINE']+strcolored[color]
    return strcolored[color]

def display_messages(string,error=False,sucess=False,info=False,sublime=False,without=False):
    if sublime:
        if   error:return  '\n{}{}[-]{} {}\n===={}\n'.format(colors['RED'],colors['BOLD'],
                                                             colors['ENDC'],string,len(string)*'=')
        elif sucess:return '\n{}{}[+]{} {}\n===={}\n'.format(colors['GREEN'],colors['BOLD'],
                                                             colors['ENDC'],string,len(string)*'=')
        elif info: return  '\n{}{}[*]{} {}\n===={}\n'.format(colors['BLUE'],colors['BOLD'],
                                                             colors['ENDC'],string,len(string)*'=')
    else:
        if   error:return  '{}{}[-]{} {}'.format(colors['RED'],colors['BOLD'],colors['ENDC'],string)
        elif sucess:return '{}{}[+]{} {}'.format(colors['GREEN'],colors['BOLD'],colors['ENDC'],string)
        elif info: return  '{}{}[*]{} {}'.format(colors['BLUE'],colors['BOLD'],colors['ENDC'],string)
