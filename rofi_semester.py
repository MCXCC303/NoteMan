# Tool project "NoteMan"

from lib.rofi import Rofi
from lib.semester import Semester
from lib import default


def semester_option():
    notebook = default.Notebook()
    semester = Semester()
    semester_options = ['Edit Snippets',
                        'Edit Header',
                        'Switch Semester',
                        'Read TextBooks',]
                        # 'New Course', TODO
                        # 'Compile All Courses', TODO

    semester_rofi = Rofi('semester-options', semester_options, prompt=f'Semester-{semester.count}')
    semester_rofi.run()
    if semester_rofi.output['selections'] == 'Edit Snippets':
        semester.edit_snippets()
    elif semester_rofi.output['selections'] == 'Edit Header':
        semester.edit_header()
    elif semester_rofi.output['selections'] == 'Read TextBooks':
        semester.read_textbook()
    elif semester_rofi.output['selections'] == 'Switch Semester':
        notebook.switch_semester()
        semester = Semester()
        semester.select_course()

semester_option()