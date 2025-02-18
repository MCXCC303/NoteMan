import shutil
from pathlib import Path
import sys
from lib.default import NOTEBOOK_ROOT
from new_lecture import create_lecture


def main():
    X = input("semester number (create as semester-X): ").strip()
    try:
        X = int(X)
    except ValueError:
        print("Error: Semester number must be an integer.")
        sys.exit(1)

    semester_dir = NOTEBOOK_ROOT / f"semester-{X}"
    if semester_dir.exists():
        print(f"Error: semester-{X} already exists.")
        sys.exit(1)
    semester_dir.mkdir()

    # header.tex should place in './'
    script_dir = Path(__file__).parent
    header_template = script_dir / "header.tex"
    if not header_template.exists():
        print("Error: header.tex template not found in script directory.")
        sys.exit(1)
    shutil.copy(header_template, semester_dir / "header.tex")

    textbooks_semester_dir = NOTEBOOK_ROOT / "TextBooks" / f"semester-{X}"
    textbooks_semester_dir.mkdir(parents=True, exist_ok=True)

    textbooks_symlink = semester_dir / "TextBooks"
    target_path = Path("../TextBooks") / f"semester-{X}"
    textbooks_symlink.symlink_to(target_path)

    print(f"Semester {X} created successfully.")
    print('New semester should include at least one lecture, create one below:')
    create_lecture(x=X)


if __name__ == "__main__":
    main()
