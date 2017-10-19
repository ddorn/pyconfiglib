import glob
import os
from pathlib import Path

import readline
HOME = str(Path.home())


def prompt_file(prompt, default=None):
    """Prompt a file name with autocompletion"""

    def complete(text: str, state):
        text = text.replace('~', HOME)

        sugg = (glob.glob(text + '*') + [None])[state]

        if sugg is None:
            return

        sugg = sugg.replace(HOME, '~')
        sugg = sugg.replace('\\', '/')

        if os.path.isdir(sugg) and not sugg.endswith('/'):
            sugg += '/'

        return sugg

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    if default is not None:
        r = input('%s [%r]: ' % (prompt, default))
    else:
        r = input('%s: ' % prompt)

    r = r or default

    # remove the autocompletion before quitting for future input()
    readline.parse_and_bind('tab: self-insert')

    return r
