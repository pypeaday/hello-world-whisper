"""This script adds subtitles to any video files missing them"""

import subprocess
from pathlib import Path

import typer
import whisper
from whisper.utils import get_writer


def return_code_has_caption(return_code: int) -> bool:
    """Converts the return code to a sensible bool"""
    if return_code == 1:
        return False
    else:
        return True


def check_for_adjacent_caption(input_file: str) -> bool:
    """Checks for an adjacent file that has a vtt extension. Indicates that captions do not need to be generated"""
    name = Path(input_file).stem
    caption_file = f"{name}.vtt"
    return Path(Path(input_file).parent, caption_file).is_file()


def check_for_embedded_caption(input_file: str) -> bool:
    """Checks if there are captions embedded in a video container"""
    subtitle_check_command = [
        "ffmpeg",
        "-i",
        input_file,
        "-c",
        "copy",
        "-map",
        "0:s:0",
        "-frames:s",
        "1",
        "-f",
        "null",
        "-",
        "-v",
        "0",
        "-hide_banner",
    ]

    process = subprocess.run(subtitle_check_command)
    if return_code_has_caption(process.returncode):
        return True
    else:
        return False


def check_for_caption(input_file: str) -> bool:
    """Check for any type of caption"""
    return check_for_adjacent_caption(input_file) or check_for_embedded_caption(
        input_file
    )


def get_list_of_videos(input_dir: str) -> list[str]:
    """Given an input directory, returns a list of paths to video files"""
    video_extensions = [".m4v", ".mp4", ".mkv"]
    video_list = []
    for path in Path(input_dir).rglob("*"):
        if path.is_file() and path.suffix in video_extensions:
            video_list.append(str(path.resolve()))

    return video_list


def generate_captions(input_dir: str, dry_run: bool = False) -> None:
    """Generates captions for video files missing them"""
    video_list = get_list_of_videos(input_dir)
    # model = whisper.load_model("base")
    model = whisper.load_model("large-v1")

    for video in video_list:
        if not check_for_caption(video):
            if dry_run:
                print(f"{video}, Missing")
            else:
                print(f"{video} Missing Caption: Generating...", end="", flush=True)

                output_path = Path(video).parent
                writer = get_writer("vtt", output_path)
                result = model.transcribe(video)
                writer(result, video)

                print("Done")
        else:
            if dry_run:
                print(f"{video}, Present")
            else:
                print(f"{video} Caption Present")


app = typer.Typer()


@app.command()
def add_captions(path: str, dryrun: bool = False):
    """Add captions to video files missing them"""
    generate_captions(path, dryrun)


if __name__ == "__main__":
    app()
