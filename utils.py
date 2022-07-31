import os
import pathlib
import shutil

from loguru import logger


def copy_anything(src, dst):
    try:
        shutil.copytree(src, dst + src.split("/")[-2])
    except Exception as err:
        logger.error(err)
        shutil.copy(src[:-1], dst)


def make_dir(path, name):
    pathlib.Path(f"{path}{name}").mkdir(parents=True, exist_ok=True)


def move_dir(original_path, target_path):
    if not pathlib.Path(original_path).is_dir():
        original_path = original_path[:-1]
    shutil.move(original_path, target_path)


def delete_anything(path):
    if not pathlib.Path(path).is_dir():
        os.remove(path[:-1])
    else:
        shutil.rmtree(path)
