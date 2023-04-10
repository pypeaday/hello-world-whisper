"""This script adds subtitles to any video files missing them"""

import argparse
import os
import subprocess

import whisper
from whisper.utils import get_writer


def return_code_has_caption(return_code: int) -> bool:
    """Converts the return code to a sensible bool"""
    if return_code == 1:
        return False
    else:
        return True


def check_for_adjacent_caption(input_file: str) -> bool:
    """Checks for an adjacent file that has a vtt extenion. Indicates that captions do not need to be generated"""
    name = os.path.splitext(input_file)
    caption_file = "{}.vtt".format(name[0])
    return os.path.isfile(caption_file)


def check_for_embedded_caption(input_file: str) -> bool:
    """Checks if there are captions embedded in a video container"""
    subtitle_check_command = f"ffmpeg -i {input_file} -c copy -map 0:s:0 -frames:s 1 -f null - -v 0 -hide_banner"

    process = subprocess.run(subtitle_check_command.split())
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
    """Given an input directory returns a list of paths to video files"""
    video_extensions = [".m4v", ".mp4", ".mkv"]
    video_list = []
    for root, _dirs, files in os.walk(input_dir):
        for name in files:
            ext = os.path.splitext(name)[1]
            if ext in video_extensions:
                video_list.append(os.path.join(root, name))

    return video_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dryrun",
        help="Show what files are missing captions",
        action="store_true",
    )
    parser.add_argument("path")
    args = parser.parse_args()

    video_list = get_list_of_videos(args.path)

    if args.dryrun:
        for video in video_list:
            if check_for_caption(video):
                print(f"{video}, Present")
            else:
                print(f"{video}, Missing")
    else:
        model = whisper.load_model("base")
        for video in video_list:
            if not check_for_caption(video):
                print(f"{video} Missing Caption: Generating...", end="", flush=True)

                output_path = os.path.dirname(video)
                writer = get_writer("vtt", output_path)
                result = model.transcribe(video)
                writer(result, video)

                print("Done")
            else:
                print(f"{video} Caption Present")
