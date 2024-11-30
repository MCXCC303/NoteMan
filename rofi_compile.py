# Tool project "NoteMan"

from lib.course import Course


def course_compile_option():
    course = Course()
    if course.compile_option():
        course.compile_lectures()
        course.read_main_pdf()


course_compile_option()
