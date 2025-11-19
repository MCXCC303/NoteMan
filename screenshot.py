import subprocess
import tempfile
import os
import shutil
from typing import Optional
from datetime import datetime


def shot_wayland(
    default_shot_dir,
    screenshot_viewer="viewnior",
    capt_tool="grim",
    scale_tool="slurp",
    shot_suffix="png",
    is_vim_editing_tex=False,
) -> Optional[str]:
    default_dir = os.path.join(default_shot_dir, capt_tool)
    os.makedirs(default_dir, exist_ok=True)
    # In wayland, use slurp to select an area
    try:
        area = subprocess.check_output([scale_tool]).decode().strip()
    except subprocess.CalledProcessError:
        return None
    with tempfile.NamedTemporaryFile(
        suffix=f".{shot_suffix}", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name
    # Use grim to take a screenshot of the selected area
    if is_vim_editing_tex:
        subprocess.run([capt_tool, "-g", area, temp_file_path])
        return temp_file_path
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        output_path = os.path.join(default_dir, f"screenshot_{timestamp}.{shot_suffix}")
        screenshot_process = subprocess.run([capt_tool, "-g", area, output_path])
        if screenshot_process.returncode:
            return None
        notify = subprocess.run(
            [
                "notify-send",
                f"{capt_tool} Screenshot saved as:",
                output_path,
                "--action=open=Open With Viewnior",
            ],
            capture_output=True,
            text=True,
        )
        if notify.returncode == 0 and notify.stdout.strip() == "open":
            subprocess.run([screenshot_viewer, output_path])
        return None


def shot_x11(
    default_shot_dir,
    screenshot_viewer="viewnior",
    capt_tool="scrot",
    shot_suffix="png",
    is_vim_editing_tex=False,
) -> Optional[str]:
    default_dir = os.path.join(default_shot_dir, capt_tool)
    os.makedirs(default_dir, exist_ok=True)
    if capt_tool == "scrot":
        temp_file_path = f"/tmp/screenshot_{capt_tool}.png"
        if is_vim_editing_tex:
            subprocess.run([capt_tool, "-s", temp_file_path])
            return temp_file_path
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            output_path = os.path.join(
                default_dir, f"screenshot_{timestamp}.{shot_suffix}"
            )
            screenshot_process = subprocess.run([capt_tool, "-s", output_path])
            if screenshot_process.returncode:
                return None
            notify = subprocess.run(
                [
                    "notify-send",
                    f"{capt_tool} Screenshot saved as:",
                    output_path,
                    "--action=open=Open With Viewnior",
                ],
                capture_output=True,
                text=True,
            )
            if notify.returncode == 0 and notify.stdout.strip() == "open":
                subprocess.run([screenshot_viewer, output_path])
            return None


def is_editing_tex() -> bool:
    try:
        vim_processes = (
            subprocess.check_output(["pgrep", "-a", "vim"]).decode().splitlines()
        )
        for process in vim_processes:
            if process.endswith(".tex") and "Notebook" in process:
                return True
    except subprocess.CalledProcessError:
        pass
    return False


def take_screenshot_to_dest(
    dest_dir,
    default_shot_dir,
    screenshot_viewer="viewnior",
    xdg_session="wayland",
    shot_suffix="png",
    is_vim_editing_tex=True,
) -> None:
    if xdg_session == "wayland":
        temp_file_path = shot_wayland(
            default_shot_dir,
            shot_suffix=shot_suffix,
            screenshot_viewer=screenshot_viewer,
            is_vim_editing_tex=is_vim_editing_tex,
        )
    else:
        temp_file_path = shot_x11(
            default_shot_dir,
            shot_suffix=shot_suffix,
            screenshot_viewer=screenshot_viewer,
            is_vim_editing_tex=is_vim_editing_tex,
        )
    # Use zenity to get new name for the screenshot
    if temp_file_path is None:
        return
    try:
        got_new_name = (
            subprocess.check_output(
                [
                    "zenity",
                    "--entry",
                    "--title=New Screenshots",
                    f"--text=Saving to {os.path.expanduser(dest_dir)}\nNew Screenshot Name: ",
                ]
            )
            .decode()
            .strip()
        )
        if got_new_name:
            destination = os.path.join(
                os.path.expanduser(dest_dir), f"{got_new_name}.{shot_suffix}"
            )
            shutil.move(temp_file_path, destination)
            notify = subprocess.run(
                [
                    "notify-send",
                    f"Screenshot saved as:",
                    destination,
                    "--action=open=Open With Viewnior",
                ],
                capture_output=True,
                text=True,
            )
            if notify.returncode == 0 and notify.stdout.strip() == "open":
                subprocess.run([screenshot_viewer, destination])
        else:
            os.remove(temp_file_path)
    except subprocess.CalledProcessError:
        os.remove(temp_file_path)


def get_xdg_session_type(capitalized=False) -> str:
    try:
        if capitalized:
            return os.environ.get("XDG_SESSION_TYPE").upper()
        else:
            return os.environ.get("XDG_SESSION_TYPE")
    except Exception:
        return "unknown"


if __name__ == "__main__":
    fig_dir = "~/Notebook/current-lecture/figures/"
    def_dir = os.path.expanduser("~/Pictures/")
    viewer = "viewnior"
    take_screenshot_to_dest(
        fig_dir,
        def_dir,
        screenshot_viewer=viewer,
        xdg_session=get_xdg_session_type(),
        is_vim_editing_tex=is_editing_tex(),
    )
