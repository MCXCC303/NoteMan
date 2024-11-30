# Tool project "NoteMan"

from lib.rofi import Rofi
from lib.course import Course
from lib import default
from lib.semester import Semester


def course_option():
    semester = Semester()
    course = Course()
    course_options = ['Edit Lecture',
                      f'Edit {default.MAIN_TEX.name}',
                      'New Lecture',
                      'Remove Lecture',
                      f'Open {default.MAIN_TEX.stem + ".pdf"}',
                      'Switch Course']

    course_rofi = Rofi('course-options', course_options, prompt=f'{''.join([word[0].upper() for word in course.course_name.split()])}')
    course_rofi.run()
    if course_rofi.output['selections'] == 'Edit Lecture':
        course.edit_lecture()
    elif course_rofi.output['selections'] == f'Edit {default.MAIN_TEX.name}':
        course.edit_main()
    elif course_rofi.output['selections'] == 'New Lecture':
        course.new_lecture()
    elif course_rofi.output['selections'] == 'Remove Lecture':
        course.remove_lecture()
    elif course_rofi.output['selections'] == f'Open {default.MAIN_TEX.stem + ".pdf"}':
        course.read_main_pdf()
    elif course_rofi.output['selections'] == 'Switch Course':
        semester.select_course()


course_option()
