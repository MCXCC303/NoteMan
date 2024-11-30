# Tool project "NoteMan"

from . import default
from pathlib import Path
import re


class Lecture(default.Notebook):
    """
    Lecture: Includes main.tex and other NUMBER.tex files

    @param self.course: course name
    @param self.semester: symlink to current semester in default
    @param self.filename: full name of file (1.tex)
    @param self.mark: stem of file (1)
    @param self.path: path to current file, change to custom course if other course name is given
    @param self.create_info: dict(header, footer) for main.tex and dict(date, number) for normal tex files
    @param self.option_showup: name to be shown in rofi

    @function __get_create_info(): generate self.create_info
    @function __beautify_showup(): generate self.option_showup
    """

    def __init__(self, filename, course=default.CURRENT_LECTURE.stem, semester=default.CURRENT_SEMESTER):
        super().__init__()
        self.course = course
        self.semester = semester
        self.filename = filename
        self.mark = Path(filename).stem
        self.path = self.root / course / self.filename
        if course != default.CURRENT_LECTURE.stem:
            self.path = self.semester / course / self.filename
        self.create_info = self.__get_create_info()
        self.option_showup = self.__beautify_showup()

    def __get_create_info(self):
        if self.mark == 'main':
            header = []
            footer = []
            part = 0
            with open(self.path) as f:
                for line in f:
                    if default.COMPILE_END_SIGN in line:
                        part = 2
                    if part == 0:
                        header.append(line.strip())
                    if part == 2:
                        footer.append(line.strip())
                    if default.COMPILE_START_SIGN in line:
                        part = 1
            return dict(header=header, footer=footer)
        # Normal Lectures
        with open(self.path) as f:
            for line in f:
                find_mark = re.search(r'\{(.*?)}\{(.*?)}', line)
                if find_mark:
                    return dict(number=find_mark.group(1), date=find_mark.group(2))
            return dict(number=self.mark, date=self.date)

    def __beautify_showup(self):
        if self.mark != 'main':
            if self.create_info['date'] != '':
                return f'<b>{self.lecture_sign.capitalize()} {self.create_info['number']}:</b> <span size="smaller">{self.create_info['date']}</span>'
            else:
                return f'<b>{self.lecture_sign.capitalize()} {self.create_info['number']}</b>'
