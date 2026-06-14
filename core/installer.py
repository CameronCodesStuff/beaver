import os
import shutil
import zipfile
import urllib.request

from core import config


def model_ready():
    return os.path.isdir(config.MODEL_PATH) and os.path.isfile(
        os.path.join(config.MODEL_PATH, "am", "final.mdl")
    )


def install_model(progress=None):
    def report(pct, msg):
        if progress:
            progress(pct, msg)

    if model_ready():
        report(100, "Model already installed.")
        return True

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
        urllib.request.urlretrieve(config.MODEL_URL, zip_path, hook)
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

    extracted = os.path.join(config.BASE_DIR, config.MODEL_FOLDER_NAME)
    if os.path.isdir(extracted):
        if os.path.isdir(config.MODEL_PATH):
            shutil.rmtree(config.MODEL_PATH)
        os.rename(extracted, config.MODEL_PATH)

    try:
        os.remove(zip_path)
    except OSError:
        pass

    if model_ready():
        report(100, "Model installed.")
        return True

    report(-1, "Model files not found after extraction.")
    return False
