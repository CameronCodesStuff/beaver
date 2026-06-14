import os
import shutil
import zipfile
import urllib.request

from core import config


def _has_vosk_files(root):
    """A valid Vosk model has an 'am/final.mdl' and a 'conf' dir somewhere under root."""
    if not os.path.isdir(root):
        return False
    for dirpath, dirnames, filenames in os.walk(root):
        if "final.mdl" in filenames:
            return True
        if "am" in dirnames and os.path.isfile(os.path.join(dirpath, "am", "final.mdl")):
            return True
    return False


def model_ready():
    return _has_vosk_files(config.MODEL_PATH)


def model_root():
    """Return the actual directory to load into Vosk (handles nested folders)."""
    if not os.path.isdir(config.MODEL_PATH):
        return config.MODEL_PATH
    # if final.mdl is directly under model/am, model/ is the root
    if os.path.isfile(os.path.join(config.MODEL_PATH, "am", "final.mdl")):
        return config.MODEL_PATH
    # otherwise find the folder that contains am/final.mdl
    for dirpath, dirnames, filenames in os.walk(config.MODEL_PATH):
        if "am" in dirnames and os.path.isfile(os.path.join(dirpath, "am", "final.mdl")):
            return dirpath
    return config.MODEL_PATH


def install_model(progress=None, large=False):
    def report(pct, msg):
        if progress:
            progress(pct, msg)

    if model_ready():
        report(100, "Model already installed.")
        return True

    url = config.MODEL_URL_LARGE if large else config.MODEL_URL
    folder = config.MODEL_FOLDER_NAME_LARGE if large else config.MODEL_FOLDER_NAME

    os.makedirs(config.BASE_DIR, exist_ok=True)
    zip_path = os.path.join(config.BASE_DIR, "_model.zip")

    report(2, "Downloading speech model…")

    def hook(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            pct = min(int(downloaded / total_size * 80) + 5, 85)
            mb = downloaded / 1024 / 1024
            report(pct, f"Downloading… {mb:.0f} MB")

    try:
        urllib.request.urlretrieve(url, zip_path, hook)
    except Exception as e:
        report(-1, f"Download failed: {e}")
        return False

    report(88, "Extracting…")
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(config.BASE_DIR)
    except Exception as e:
        report(-1, f"Extract failed: {e}")
        return False

    extracted = os.path.join(config.BASE_DIR, folder)
    if os.path.isdir(extracted) and extracted != config.MODEL_PATH:
        if os.path.isdir(config.MODEL_PATH):
            shutil.rmtree(config.MODEL_PATH)
        try:
            os.rename(extracted, config.MODEL_PATH)
        except OSError:
            shutil.move(extracted, config.MODEL_PATH)

    try:
        os.remove(zip_path)
    except OSError:
        pass

    if model_ready():
        report(100, "Model installed.")
        return True

    report(-1, "Model files not found after extraction.")
    return False
