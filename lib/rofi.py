# Tool project "NoteMan"

import subprocess

THEME_PATH = "/home/thf/Programme/Python/NoteMan/theme/"

class Rofi:
    """
    Rofi: Refined dmenu class based on Gilles Castel

    @param session_name: name theme file in 'session_name.rasi'
    @param options: str list
    @param prompt: a hint of each window
    @param fuzzy: enable fuzzy search
    @param multi_select
    @param theme: enable custom theme
    @param theme_path
    @param extra_args
    @param self.output: [selections, key, index]

    @function run(): start a rofi menu and store status and selections in self.output
    """

    def __init__(self, session_name, options, prompt='NoteMan', lines=7, fuzzy=False, multi_select=False, theme=True,
                 theme_path=THEME_PATH, extra_args=None):
        self.session_name = session_name
        self.options = options
        self.prompt = prompt
        self.fuzzy = fuzzy
        self.multi_select = multi_select
        self.theme = theme
        self.lines = lines
        self.theme_path = theme_path
        self.extra_args = extra_args
        self.output = None
        self.rofi_args = None
        if extra_args is None:
            self.extra_args = []

    def run(self):
        rofi_options = '\n'.join(self.options)
        args = ['rofi', '-dmenu']  # Base of rofi
        args += ['-markup-rows', '-sort']
        args += ['-p', self.prompt]
        args += ['-l', self.lines]
        args += ['-format', 's', '-i']
        args += self.extra_args
        if self.fuzzy:
            args += ['-matching', 'fuzzy']
        if self.multi_select:
            args += ['-multi-select']
        if self.theme:
            args += ['-theme', self.theme_path + self.session_name + '.rasi']
        args = [str(arg) for arg in args]
        self.rofi_args = args  # Debug

        result = subprocess.run(self.rofi_args, input=rofi_options, stdout=subprocess.PIPE, universal_newlines=True)
        return_code = result.returncode
        stdout = result.stdout.strip()
        selections = stdout.strip()

        # Castel's Code
        # index = -1: no selection, selection not found or multi-select
        try:
            index = [opt.strip() for opt in self.options].index(selections)
        except ValueError:
            index = -1
        if return_code == 0:
            key = 0
        elif return_code == 1:
            key = -1
        else:
            key = return_code - 9

        self.output = dict(selections=selections, index=index, key=key)
