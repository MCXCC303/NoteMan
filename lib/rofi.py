# Tool project "NoteMan"

import subprocess


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

    def __init__(
        self,
        session_name: str,
        options: list,
        prompt: str = "NoteMan",
        theme_path: str = "/home/thf/Programme/Python/NoteMan/theme/",
        lines: int = 7,
        use_fuzzy_search=False,
        multi_select_enabled=False,
        theme_enabled=True,
        extra_args: list[str] = [],
        confirm_window=False,
    ):
        self._confirm_window = confirm_window
        if self._confirm_window:
            self.session_name = session_name
            self._theme_enabled = theme_enabled
            self.prompt = prompt
            self.theme_path = theme_path
            self.lines = lines
            self.options = options
            return
        self.session_name = session_name
        self.options = options
        self.prompt = prompt
        self.lines = lines
        self.theme_path = theme_path
        self._use_fuzzy_search = use_fuzzy_search
        self._multi_select_enabled = multi_select_enabled
        self._theme_enabled = theme_enabled
        self._extra_args = extra_args
        self.output = None
        self.rofi_args = None

    def run(self):
        if self._confirm_window:
            raise AttributeError
        rofi_options = "\n".join(self.options)
        args = ["rofi", "-dmenu"]  # Base of rofi
        args += ["-markup-rows", "-sort"]
        args += ["-p", self.prompt]
        args += ["-l", self.lines]
        args += ["-format", "s", "-i"]
        args += self._extra_args
        if self._use_fuzzy_search:
            args += ["-matching", "fuzzy"]
        if self._multi_select_enabled:
            args += ["-multi-select"]
        if self._theme_enabled:
            args += ["-theme", self.theme_path + self.session_name + ".rasi"]
        args = [str(arg) for arg in args]
        self.rofi_args = args  # Debug

        result = subprocess.run(
            self.rofi_args,
            input=rofi_options,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
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

    def run_confirm(self):
        if not self._confirm_window:
            raise AttributeError
        buttons = f"{self.options[0]}\n{self.options[1]}"
        args = ["rofi", "-dmenu"]  # Base of rofi
        args += ["-p", self.prompt]
        args += ["-mesg", self.prompt]
        args += [
            "-theme-str",
            "textbox {horizontal-align: 0.5;}",
            "-theme-str",
            "listview {columns: 2; lines: 1;}",
            "-theme-str",
            'mainbox {children: ["message", "listview"];}',
        ]
        if self._theme_enabled:
            args += ["-theme", self.theme_path + self.session_name + ".rasi"]
        self.rofi_args = args  # Debug
        result = subprocess.run(
            self.rofi_args,
            input=buttons,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        return_code = result.returncode
        stdout = result.stdout.strip()
        if return_code == 0:
            self.confirm_result = stdout
            return
        self.confirm_result = self.options[1]
