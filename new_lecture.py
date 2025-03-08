import os
import sys
from lib.default import CURRENT_LECTURE,CURRENT_SEMESTER
from lib.default import NOTEBOOK_ROOT
from lib.course import Course

# NOTEBOOK_ROOT = Path('/home/thf/Homework')
# CURRENT_LECTURE = NOTEBOOK_ROOT / 'current-lecture'
# CURRENT_SEMESTER = NOTEBOOK_ROOT / 'current-semester'

def int_to_roman(num):
    if num == 0:
        return 'I'
    if not isinstance(num, int) or num < 1 or num > 3999:
        raise ValueError("Number must be an integer between 1 and 3999")

    val_sym = [
        (1000, 'M'), (900, 'CM'),
        (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'),
        (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'),
        (5, 'V'), (4, 'IV'),
        (1, 'I')
    ]

    roman_num = ''
    for value, symbol in val_sym:
        while num >= value:
            roman_num += symbol
            num -= value
    return roman_num

def create_lecture(x=None):
    if x is not None:
        X = str(x)
    else:
        X = input("semester number (create in semester-X): ").strip()
    try:
        X = int(X)
    except ValueError:
        print("Error: Semester number must be an integer.")
        sys.exit(1)

    semester_dir = NOTEBOOK_ROOT / f"semester-{X}"
    if not semester_dir.exists():
        print(f"Error: semester-{X} does not exist.")
        sys.exit(1)
    os.remove(CURRENT_SEMESTER)
    CURRENT_SEMESTER.symlink_to(semester_dir)

    lecture_name = input("lecture name: ").strip()
    if not lecture_name:
        print("Error: Lecture name cannot be empty.")
        sys.exit(1)

    lecture_dir = semester_dir / lecture_name
    if lecture_dir.exists():
        print(f"Error: Lecture '{lecture_name}' already exists in semester {X}.")
        sys.exit(1)

    # Get info
    lecturer = input("lecturer: ").strip()
    noter = input("noter (default: THF): ").strip() or "THF"
    className = input(f"className (default: {lecture_name}): ").strip() or lecture_name
    if X == 0:
        term = input(f"term (default {int_to_roman(X)}-A): ").strip() or int_to_roman(X)
    else:
        term = input(f"term (default {int_to_roman(X)}-B): ").strip() or int_to_roman(X)

    lecture_dir.mkdir()
    if CURRENT_LECTURE.exists():
        os.remove(CURRENT_LECTURE)
    CURRENT_LECTURE.symlink_to(lecture_dir)

    MAIN_TEX_CONTENT = f"""%─────────────────%
% Header Settings %
%─────────────────%
\\def\\lecturer{{{lecturer}}}
\\def\\noter{{{noter}}}
\\def\\className{{{className}}}
\\def\\term{{{term}}}
\\input{{../header}}

%──────────%
% Document %
%──────────%
\\begin{{document}}
\\maketitle
\\tableofcontents
% Compile start
\\input{{1}}
% Compile end
\\end{{document}}
"""

    (lecture_dir / "main.tex").write_text(MAIN_TEX_CONTENT)
    # (lecture_dir / "1.tex").touch()
    figures_dir = lecture_dir / "figures"
    figures_dir.mkdir()

    textbooks_lecture_dir = NOTEBOOK_ROOT / "TextBooks" / f"semester-{X}" / lecture_name
    textbooks_lecture_dir.mkdir(parents=True, exist_ok=True)

    relative_path = os.path.relpath(textbooks_lecture_dir, lecture_dir)
    textbooks_symlink = lecture_dir / "TextBooks"
    textbooks_symlink.symlink_to(relative_path)

    print(f"Lecture '{lecture_name}' created successfully in semester-{X}.")
    Course().new_lecture(filename='1')


if __name__ == "__main__":
    create_lecture()
