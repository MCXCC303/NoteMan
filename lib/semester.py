# Tool project "NoteMan"

from . import default
from .rofi import Rofi
from pathlib import Path
import os


class Semester(default.Notebook):
    """
    Semester: Sub-grade of Notebook root

    @param self.path: $NOTEBOOK_PATH/semester-X, extract from symbol link in default
    @param self.count: X
    @param self.sub_strs: In this class stands for courses of this semester
    @param self._textbooks: [options_in_rofi, full_path_of_textbook]
    @param self._snippets: options_in_rofi
    @param self._courses: course_strs without header and TextBooks

    @function edit_header()
    @function edit_snippet()
    @function read_textbook()
    @function select_course()
    """

    def __init__(self):
        super().__init__()
        self.path = self.root / Path(os.readlink(default.CURRENT_SEMESTER)).stem
        self.count = self.path.stem.split('-')[-1]
        self.__textbooks = self.__get_textbooks()
        self.__snippets = self.__get_snippets()
        self.__courses = self.__get_courses()

    def __get_courses(self):
        course_strs = self._get_sub_strs(self.path)
        course_strs.remove('header')
        course_strs.remove('TextBooks')
        return course_strs

    def __get_textbooks(self):
        textbook_path = self.path / 'TextBooks'
        books = [str(book).split('/')[-2:] for book in textbook_path.rglob('*')]
        textbook_options = []
        for i in range(len(books)):
            if 'TextBooks' not in books[i]:
                textbook_options.append(books[i])
        books = textbook_options
        for i in range(len(textbook_options)):
            textbook_options[i] = '/'.join(textbook_options[i])
        return [textbook_options, books]

    def __get_snippets(self):
        snippet_path = self.root / 'UltiSnips'
        snippets = self._get_sub_strs(snippet_path)
        return snippets

    def edit_header(self, header='header'):
        self._edit(self.path / (header + '.tex'))

    def edit_snippets(self):
        select_snippet = Rofi('get-snippet', self.__snippets, prompt='Snippets', lines=5)
        select_snippet.run()
        if select_snippet.output['index'] != -1:
            self._edit(self.root / 'UltiSnips' / (select_snippet.output['selections'] + '.snippets'))

    def read_textbook(self):
        select_textbook = Rofi('read-textbook', self.__textbooks[0], prompt='Textbook', lines=9)
        select_textbook.run()
        if select_textbook.output['index'] != -1:
            textbook_fullname = str(self.__textbooks[1][select_textbook.output['index']])
            reader = self._choose_reader(Path(textbook_fullname))
            self._read(self.path / 'TextBooks' / textbook_fullname,
                       reader=reader)

    def select_course(self):
        select_lecture = Rofi('select-course', self.__courses, prompt='Courses', lines=9)
        select_lecture.run()
        os.remove(default.CURRENT_LECTURE)
        if select_lecture.output['index'] != -1:
            os.symlink(self.path / select_lecture.output['selections'], default.CURRENT_LECTURE)
        else:
            os.symlink(self.path / self.__courses[0], default.CURRENT_LECTURE)
