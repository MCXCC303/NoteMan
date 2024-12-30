# Tool project "NoteMan"

from lib.course import Course


def course_compile_option():
    course = Course()
    if course.compile_option():
        course.compile_lectures()


course_compile_option()
