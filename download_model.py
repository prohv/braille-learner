import urllib.request
import tarfile
import os
import sys


VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR = "models/vosk-model-small-en-us-0.15"
ZIP_FILE = "vosk-model.zip"


def download_with_progress(url, filename):
    print(f"Downloading from {url}...")

    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rProgress: {min(percent, 100)}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, filename, progress_hook)
    print("\nDownload complete!")


def extract_model(zip_file, extract_to):
    print(f"Extracting {zip_file}...")

    import zipfile

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    print("Extraction complete!")


def main():
    if not os.path.exists("models"):
        os.makedirs("models")

    if os.path.exists(MODEL_DIR):
        print(f"Model already exists at {MODEL_DIR}")
        return

    try:
        download_with_progress(VOSK_MODEL_URL, ZIP_FILE)
        extract_model(ZIP_FILE, "models")

        os.remove(ZIP_FILE)
        print("Cleanup complete!")
        print(f"\nModel successfully installed at {MODEL_DIR}")

    except Exception as e:
        print(f"\nError during download: {e}")
        print("Please try downloading manually:")
        print(f"1. Download from: {VOSK_MODEL_URL}")
        print(f"2. Extract to: {MODEL_DIR}")


if __name__ == "__main__":
    main()
