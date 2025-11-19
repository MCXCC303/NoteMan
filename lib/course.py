# Tool project "NoteMan"

import sys
from . import default
from .lecture import Lecture
from .rofi import Rofi
from natsort import natsorted
from pathlib import Path
import os


class Course(default.Notebook):
    """
    Course: Any course in any semester, include lecture files (1.tex), main.tex, and a main.pdf

    @note It is suggested to refine your default sign format, I use '\\lecture{$1}{$2}' in normal courses and '\\learn{$1}{$2}' in self-leaning courses.

    @param self.course_name
    @param self.path
    @param self.semester
    @param self.__compiles: compile list after parsed, ['\\input{1}']
    @param self.__lecture_amount: use to scale the natural input
    @param self.__lectures: '.tex' and no-extension styles provided, ['Rofi option list', 'mark list', 'full-name list', 'Rofi option list (number file only)', 'number list', 'full-name list (number only)', 'Lecture object list', 'Lecture object list (number only)']
    @param self.__main_tex: Lecture obj of main.tex

    @function edit_lecture()
    @function edit_main()
    @function new_lecture()
    @function remove_lecture()
    @function read_main_pdf()
    @function compile_option()
    @function compile_lectures()

    @see lecture.Lecture
    """

    def __init__(self, course_custom=True, semester=default.CURRENT_SEMESTER):
        super().__init__()
        self.semester = semester
        self.course_name = default.CURRENT_LECTURE.name
        self.path = default.CURRENT_LECTURE
        if course_custom:
            self.course_name = Path(os.readlink(default.CURRENT_LECTURE)).name
            self.path = default.CURRENT_SEMESTER / self.course_name
        self.__compiles = None
        self.__lectures = self.__get_lectures()
        self.__lecture_amount = len(self.__lectures[0])
        self.__main_tex = Lecture(f"{default.MAIN_TEX.name}")

    def __get_lectures(self):
        lecture_file_stems = self._get_sub_strs(self.path, file_format="*.tex")
        lecture_file_stems.remove("main")  # still have non-number files
        lecture_file_stems_number_only = []  # number only, use in compile
        for stem in lecture_file_stems:
            if str(stem).isdigit():
                lecture_file_stems_number_only.append(int(stem))

        lectures = []
        for lecture_stem in natsorted(lecture_file_stems):
            lec_obj = Lecture(f"{lecture_stem}.tex", course=self.course_name)
            lectures.append(lec_obj)

        lectures_number_only = []
        for lecture_stem in natsorted(lecture_file_stems_number_only):
            lec_obj = Lecture(f"{lecture_stem}.tex", course=self.course_name)
            lectures_number_only.append(lec_obj)

        __lectures = [
            list(reversed([lec_obj.option_showup for lec_obj in lectures])),
            natsorted([lec_stem for lec_stem in lecture_file_stems], reverse=True),
            natsorted(
                [f"{lec_stem}.tex" for lec_stem in lecture_file_stems], reverse=True
            ),
            list(reversed([lec_obj.option_showup for lec_obj in lectures_number_only])),
            natsorted(
                [lec_stem for lec_stem in lecture_file_stems_number_only], reverse=True
            ),
            natsorted(
                [f"{lec_stem}.tex" for lec_stem in lecture_file_stems_number_only],
                reverse=True,
            ),
            lectures,
            lectures_number_only,
        ]
        return __lectures

    def __parse_range_string(self, arg):
        range_strings = arg.strip().split(",")
        range_list = set()

        for pace in range_strings:
            pace = pace.strip()
            if "-" in pace:
                start, end = pace.split("-")
                if int(end) <= self.__lecture_amount:
                    range_list.update(range(int(start), int(end) + 1))
                else:
                    range_list.update(range(int(start), int(self.__lecture_amount)))
            else:
                if int(pace) <= self.__lecture_amount:
                    range_list.add(int(pace))
        lec_list = natsorted(list(range_list))
        return [self._parse_lecture_spec(lec) for lec in lec_list]

    def __choose_to_compile(self):
        multi_select_compile = Rofi(
            "multi-select-compile", self.__lectures[3], multi_select_enabled=True
        )
        multi_select_compile.run()
        if multi_select_compile.output["selections"] != "":
            selections = [
                list(reversed(self.__lectures[3])).index(selection) + 1
                for selection in multi_select_compile.output["selections"].split("\n")
            ]
            return list(reversed(selections))
        return None

    def __parse_compile_args(self, options):
        if options == "All":
            compiles = [
                self._parse_lecture_spec(lec)
                for lec in list(reversed(self.__lectures[4]))
            ]
            return compiles
        elif options == "Latest":
            return [self._parse_lecture_spec(self.__lectures[4][0])]
        elif options == "Latest Two":
            return [
                self._parse_lecture_spec(lec)
                for lec in list(reversed(self.__lectures[4][:2]))
            ]
        elif options == "Choose To Compile":
            multi_selections = self.__choose_to_compile()
            if multi_selections is not None:
                return [self._parse_lecture_spec(lec) for lec in multi_selections]
        elif options != "":  # natural input
            return self.__parse_range_string(options)

    def compile_option(self, option=None):
        if option is not None:
            self.__compiles = self.__parse_compile_args(option)
            return True
        compile_options = ["All", "Latest", "Latest Two", "Choose To Compile"]
        select_compile = Rofi("select-compile", compile_options, prompt="Compile")
        select_compile.run()
        if select_compile.output["selections"] != "":
            self.__compiles = self.__parse_compile_args(
                select_compile.output["selections"]
            )
            if self.__compiles is not None:
                return True

    def read_main_pdf(self):
        self._read(self.path / "main.pdf")

    def edit_lecture(self):
        select_lecture = Rofi("select-lecture", self.__lectures[0], prompt="Lecture")
        select_lecture.run()
        if (
            select_lecture.output["selections"] != ""
            and select_lecture.output["index"] != -1
        ):
            self._edit(self.path / self.__lectures[2][select_lecture.output["index"]])
        elif select_lecture.output["selections"] != "":
            self.new_lecture(filename=select_lecture.output["selections"])

    def edit_main(self):
        self._edit(self.path / "main.tex")

    def new_lecture(self, filename=None):
        if filename is None:
            new_lecture_num = str(int(self.__lectures[4][0]) + 1)
            new_lecture_file = f"{new_lecture_num}.tex"
            self.path.touch(new_lecture_file)
            (self.path / new_lecture_file).write_text(
                f"\\{self.lecture_sign}{{{new_lecture_num}}}{{{self.date}}}"
            )
        else:
            new_lecture_file = f"{filename}.tex"
            self.path.touch(new_lecture_file)
            (self.path / new_lecture_file).write_text(
                f"\\{self.lecture_sign}{{{filename}}}{{{self.date}}}"
            )
        self.__init__()
        self._edit(self.path / new_lecture_file)
        self.compile_option("Latest Two")
        self.compile_lectures()
        # self.read_main_pdf()

    def remove_lecture(self, file=None):
        if file is not None:
            os.remove(self.path / file)
            return
        remove_lecture = Rofi("remove-lecture", self.__lectures[0], prompt="Remove")
        remove_lecture.run()
        if remove_lecture.output['selections'] == '':
            return
        confirm_remove = Rofi("confirm-remove", ['Yes', 'No'], confirm_window=True, prompt=f"Comfirm Delete {remove_lecture.output['selections']}?")
        confirm_remove.run_confirm()
        if confirm_remove.confirm_result == 'No':
            return
        if remove_lecture.output["selections"] != "":
            os.remove(
                str(self.path / self.__lectures[2][remove_lecture.output["index"]])
            )

    def compile_lectures(self):
        main_tex = self.__main_tex.create_info["header"]
        main_tex += self.__compiles
        main_tex += self.__main_tex.create_info["footer"]
        self.remove_lecture(file=default.MAIN_TEX)
        self.path.touch(default.MAIN_TEX)
        (self.path / default.MAIN_TEX).write_text("\n".join(main_tex))
        self._latex_compile()
