import sys
import upload_procs
import utils
from pathlib import Path
import post_procs
import upload_procs

sd = utils.samples_dir()
samples = list(sd.glob("*"))


def sample_exists(name):
    for sample in samples:
        if sample.stem == name:
            return True

    return False


for post in post_procs.get_postlist():
    if sample_exists(post.name):
        continue

    path = utils.files_dir() / Path(post.name + "." + post.ext)

    if post.mtype.startswith("image"):
        upload_procs.get_image_sample(path)
    elif post.mtype.startswith("video"):
        upload_procs.get_video_sample(path)
    elif post.mtype.startswith("audio"):
        upload_procs.get_audio_sample(path)
    elif utils.is_text_file(path):
        upload_procs.get_text_sample(path)