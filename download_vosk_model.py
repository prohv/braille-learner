"""Download Vosk English model for offline speech recognition.

Downloads the small English model optimized for constrained vocabulary recognition.
This model is ideal for single-letter recognition on Raspberry Pi.
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path


MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR = "models/vosk-model-small-en-us-0.15"
ZIP_FILENAME = "vosk-model.zip"


class DownloadProgress:
    """Simple progress reporter for downloads."""

    def __init__(self):
        self.downloaded = 0
        self.total = 0
        self.last_percent = -1

    def __call__(self, block_num, block_size, total_size):
        self.downloaded = block_num * block_size
        self.total = total_size

        if total_size > 0:
            percent = int((self.downloaded / total_size) * 100)
            if percent != self.last_percent and percent % 5 == 0:
                mb_downloaded = self.downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(
                    f"  Progress: {percent}% ({mb_downloaded:.1f} / {mb_total:.1f} MB)"
                )
                self.last_percent = percent


def download_model():
    """Download and extract Vosk model."""

    # Check if already exists
    if Path(MODEL_DIR).exists():
        print(f"Vosk model already exists at {MODEL_DIR}")
        print("To re-download, delete this directory first.")
        return True

    # Create models directory
    Path("models").mkdir(exist_ok=True)

    print("=" * 60)
    print("Vosk Model Downloader")
    print("=" * 60)
    print()
    print(f"Model: {MODEL_URL}")
    print(f"Target: {MODEL_DIR}")
    print()

    # Download
    print("Downloading...")
    try:
        progress = DownloadProgress()
        urllib.request.urlretrieve(MODEL_URL, ZIP_FILENAME, reporthook=progress)
        print("Download complete!")
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("\nPlease download manually:")
        print(f"1. Visit: https://alphacephei.com/vosk/models")
        print(f"2. Download: vosk-model-small-en-us-0.15.zip")
        print(f"3. Extract to: {MODEL_DIR}")
        return False

    # Extract
    print("\nExtracting...")
    try:
        with zipfile.ZipFile(ZIP_FILENAME, "r") as zip_ref:
            zip_ref.extractall("models")
        print("Extraction complete!")
    except Exception as e:
        print(f"Error extracting model: {e}")
        return False

    # Cleanup
    try:
        os.remove(ZIP_FILENAME)
        print("Cleaned up temporary files.")
    except:
        pass

    # Verify
    if Path(MODEL_DIR).exists():
        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Model installed at: {MODEL_DIR}")
        print()
        print("You can now run the application:")
        print("  python main.py --simulate")
        return True
    else:
        print()
        print("ERROR: Model extraction failed.")
        return False


if __name__ == "__main__":
    try:
        success = download_model()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        # Cleanup partial download
        if Path(ZIP_FILENAME).exists():
            try:
                os.remove(ZIP_FILENAME)
            except:
                pass
        sys.exit(1)
