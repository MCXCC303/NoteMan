# Tool project "NoteMan"

from .rofi import Rofi
from datetime import datetime
from natsort import natsorted
from pathlib import Path
import os
import re
import subprocess

NOTEBOOK_ROOT = Path('~/Notebook').expanduser()
NOTER = 'THF'
CURRENT_SEMESTER = NOTEBOOK_ROOT / 'current-semester'
CURRENT_LECTURE = NOTEBOOK_ROOT / 'current-lecture'
# DATE_FORMAT = '%a %d %b %Y %H:%M'
DATE_FORMAT = '%m.%d'
MAIN_TEX = Path('main.tex')
HEADER_TEX = Path('header.tex')
COMPILE_START_SIGN = 'Compile start'
COMPILE_END_SIGN = 'Compile end'
LECTURE_SIGN = 'lecture'
SEARCH_SIGN = True
LECTURE_SIGN_SEARCH_PATTERN = r'{\\[a-zA-Z]+}'
LATEX_COMPILE_ARGS = ['latexmk', '-xelatex', '-verbose', '-file-line-error', '-synctex=1', '-interaction=nonstopmode']


class Notebook:
    """
    Notebook: Extended class extracted from semester (root)

    @param self.root: the root path of Notebook, '/home/user/Notebook' in default
    @param self.current_lecture: a symbol link to current lecture
    @param self.current_semester: a symbol link to current semester
    @param self.date: get current date, format in 'month.date' style and is used to recognize lectures
    @param self.__semesters
    @param self.lecture_sign: could be 'lecture', 'learn' and 'homework' etc.

    @function switch_semester()
    @function __patch_lecture_sign(): search in header.tex to find custom sign of lectures, you need to append '% lecture sign' to your own sign command in header.tex
    @function _latex_compile(): compile from main.tex, controlled by course_path
    @function _get_sub_strs(): interface for scan text
    @function _edit(): interface for editing
    @function _read(): interface for opening pdf file
    @function _parse_lecture_spec(): '1' -> '\\input{1}'
    """

    def __init__(self):
        self.root = NOTEBOOK_ROOT
        self.date = datetime.today().strftime(DATE_FORMAT)
        self.current_lecture = CURRENT_LECTURE
        self.current_semester = CURRENT_SEMESTER
        self.__semesters = self.__get_semesters()
        if SEARCH_SIGN:
            self.lecture_sign = self._patch_lecture_sign()

    @staticmethod
    def _patch_lecture_sign():
        with open(CURRENT_SEMESTER / HEADER_TEX) as f:
            for line in f:
                if 'lecture sign' in line:
                    lecture_sign = re.search(LECTURE_SIGN_SEARCH_PATTERN, line).group(0)[2:-1]
                    return lecture_sign
            else:
                return LECTURE_SIGN

    @staticmethod
    def _latex_compile(course_path=CURRENT_LECTURE, main_tex_file=MAIN_TEX.name):
        latex_compile_args = LATEX_COMPILE_ARGS
        latex_compile_args.append(main_tex_file)
        result = subprocess.run(latex_compile_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                cwd=str(course_path))
        return result.returncode  # Optional

    @staticmethod
    def _get_sub_strs(path, file_format='*', extended=False):
        if extended:
            sub_strs = [sub_str.name for sub_str in path.glob(file_format)]
        else:
            sub_strs = [sub_str.stem for sub_str in path.glob(file_format)]
        return sub_strs

    @staticmethod
    def _edit(file, editor="vim", term_win=None, vim_args=None):
        if vim_args is None:
            vim_args = ['--servername', 'THF', '--remote-silent']
        if term_win is None:
            term_win = ["alacritty", "--command"]
        edit_open_args = term_win
        edit_open_args += [editor, f"{file}"]
        subprocess.Popen(edit_open_args)

    @staticmethod
    def _read(pdf_file, reader="zathura"):
        read_args = [reader, pdf_file]
        subprocess.Popen(read_args)

    @staticmethod
    def _parse_lecture_spec(number):
        return f'\\input{{{number}}}'

    def __get_semesters(self):
        semesters = self._get_sub_strs(self.root, file_format='semester-*')
        return natsorted(semesters, reverse=True)

    def switch_semester(self):
        select_semester = Rofi('select-semester', self.__semesters, prompt='Select')
        select_semester.run()
        if select_semester.output['selections'] != '':
            os.remove(CURRENT_SEMESTER)
            os.symlink(self.root / select_semester.output['selections'], CURRENT_SEMESTER)
