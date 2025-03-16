import utils
import post_procs
import sample_procs
from pathlib import Path

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

    try:
        if post.mtype.startswith("image"):
            sample_procs.get_image_sample(path)
        elif post.mtype.startswith("video"):
            sample_procs.get_video_sample(path)
        elif post.mtype.startswith("audio"):
            sample_procs.get_audio_sample(path)
        elif utils.is_text_file(path):
            sample_procs.get_text_sample(path)
    except Exception:
        pass
