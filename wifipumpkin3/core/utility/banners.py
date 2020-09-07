import random

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

wp_banner = {}

wp_banner[
    "default"
] = r"""
  _      ___ _____     ___                  __    _      ____
 | | /| / (_) __(_)___/ _ \__ ____ _  ___  / /__ (_)__  |_  /
 | |/ |/ / / _// /___/ ___/ // /  ' \/ _ \/  '_// / _ \_/_ < 
 |__/|__/_/_/ /_/   /_/   \_,_/_/_/_/ .__/_/\_\/_/_//_/____/ 
                                   /_/                       
                                            codename: {}"""

# from https://asciiart.website/index.php?art=holiday/halloween
wp_banner[
    "halloween"
] = '''
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$PR$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$"    @$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$"      '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$                 """"""#*R$$$$$$$$$$$$$
$$$$$$$$$$$$$P"..::!~ .....    .<!!!!!!!:  ~!!!:.. "*$$$$$$$$$
$$$$$$$$$$".<!!!!~  <!!!!!!!~ !!!!!!!!!!!!!  !!!!!!!: "$$$$$$$
$$$$$$$P <!!!!!~ .!!!!!!!!!! !!!!!!!!!!!!!!!. `!!!!!!!: "$$$$$
$$$$$P :!!!!!~ .!!!!~!!!!!! .!!!!!!!!!~!!!!!!: '!!!!!!!! '$$$$
$$$$# !!!!!f  !!!`   `!!!!! :!!!!!!!!!    `!!!! `!!!!!!!! '$$$
$$$F !!!!!!  !!~      '!!!f  4!!!!!!!!       !!> 4!!!!!!!> 9$$
$$P <!!!!!  !!>        '!!~   '!!!!!!........<!!  !!!!!!!! <$$
$$> !!!!!! ~!!!!!!!!!!!!!~      `!!!!!!!!!!!!!!!> `!!!!!!!  $$
$$ '!!!!!! '!!!!!!!!!!!!!!> !!!!!!!!!!!!!!(``~!!!  !!!!!!f 4$$
$$r!!!!!!! `!!~   :<!!!!!!! `!!!!!!!!!!!!!~    `! '!!!!!!> .$$
$$L !!!!!!. !!:h   `!!!!!!! `!!!!!!!!!~     <!!!!  !!!!!!  @$$
$$$ `!!!!!! ~!!!!       `~~ '~~~~~`        !!!!!f .!!!!!  <$$$
$$$N ~!!!!!! !!!!!h.           ..::     .!!!!!!!  :!!!!` .$$$$
$$$$$. ~!!!!> !!!!!!!!:       `!!!!!h!!!!!!!!!!~  !!!!  d$$$$$
$$$$$$N. `!!!. !!!!!!!!!!!!! ~!!!!!!!!!!!!!!!!~  !!~ .e$$$$$$$
$$$$$$$$$bu  `  '!!!!!!!!!!~  !!!!!!!!!!!!!~` .uuue$$$$$$$$$$$
$$$$$$$$$$$$$$$$e.  ````   wifi     ```   .e$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                                            codename: {}'''

# from https://ascii.co.uk/art/pumpkin
wp_banner[
    "pumpkin"
] = """
                            .,'
                        .''.'
                        .' .'
            _.ood0Pp._ ,'  `.~ .q?00doo._
        .od00Pd0000Pdb._. . _:db?000b?000bo.
     .?000Pd0000Pd0000PdbMb?0000b?000b?0000b.
    .d0000Pd0000Pd0000Pd0000b?0000b?000b?0000b.
    d0000Pd0000Pd00000Pd0000b?00000b?0000b?000b.
    00000Pd0000Pd0000Pd00000b?00000b?0000b?0000b
    ?0000b?0000b?  WiFiPumpkin3  00Pd0000Pd0000P
    ?0000b?0000b?0000b?00000Pd00000Pd0000Pd000P
    `?0000b?0000b?0000b?0000Pd0000Pd0000Pd000P'
     `?000b?0000b?000b?0000Pd000Pd0000Pd000P
        `~?00b?000b?000b?000Pd00Pd000Pd00P'
            `~?0b?0b?000b?0Pd0Pd000PdP~'
                                     codename: {}"""

# from https://ascii.co.uk/art/pumpkin
wp_banner[
    "pumpkin2"
] = """
                            .,'
                        .''.'
                        .' .'
            .    ' . ~,'  `.~ . `    .
        . '  .  '   .`:_. . _:'.   `  .  ` .
    .'   .'     ,     .'^'.    .     `.   `.
    .    .       .A.  .     . .A.       .    .
                .d000b.      .d000b.
    '    '    .d0000000b.  .d0000000b.    `    `
    .    .      .      . db  .     .      .    .
                        d00b
    `    `?0o.  `     `     '    '  .o0P'    '
        .    `?00   ooooo.  .ooooo   00P' .   .
        ` .   `?00000P ?0bd0P ?00000P' .' . '
            . . `~~   ~~~~  .~~'  . .
                ~     - ~~ -    ~
                                  codename: {}"""


# from https://textart.sh/topic/pumpkin
wp_banner[
    "textart"
] = r"""
                             Jgy__
                            jWW  `""9Wf
                          _#WWW     IW
                         jWWWWW     IW
                 __,yyyyyWWWWW     IWyyyy___
            _jyWWP"^``"`.C"9*,J _.mqD:^^"WWWWWWQg__
          jgW"^.C/"    .C'     I    `D.     'D._"WQg_
        jWP` .C"       C'      I     `D._     `D._ "Qg_
      jQP`  .C    ,d^^b._      I      _.d^^b.   `D._ "Qg
     jQ^  .C"   /`   .+" \     I     / "+.   `\   `D.  XQ
    jQ'  .C'   |`  ."    )    _I    (     ".  |    `D.  4#
    Qf  .C     (   (    /    / /\    \     )  )     `D.  Qg
   jW   C'      \__\_.+'    / /  \    `+._/__/       `D  jQ
   Qf   C         C        /_/    \         D         D   Qk
   Qf   C      _  C        \_\____/         D  _      D   QF
   QL   C      \`+.__     _______     ______.+'/      D   QF
   B&   C.      \   \|    ||     |    ||      /       D   Qf
   jQ   `C.      \   |____|/     |____|/__   /      .D'   jW
    TQ   `C.      \._   `+.__________/___/|_/      .D'   jQ`
     9Q   `C.      C.`+._           |   |/.D'     .D'   jQ'
      "Qg  `C.     `C.   `"+-------'   ' .D'     .D'   pW`
       ^WQy `C.     `C.        I        .D'    _.D' yW"
         ^9Qy_`C.    `C.       I       .D'   _.D jgW"
            `9WQgC.__ `C.      I      .D'  _.Dp@@"`
           ilmk `""9WQQggyyyyyygyyyyyQggQWQH""
                                            codename: {}"""


def random_banners():
    return wp_banner.get(random.choice(list(wp_banner.keys())))
