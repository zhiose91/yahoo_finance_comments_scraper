import requests
import shutil
import re
import os
import sys
import zipfile
import ctypes
from contextlib import closing
import io


def download_driver(chrome_version=None, file=__file__):
    """ Get Chrome version then get matched driver online
    Args:
    Returns:
    """

    print("Downloading corresponding chromedriver")
    driver_storage_link = "https://chromedriver.storage.googleapis.com"

    if not chrome_version:
        if sys.platform == "win32":
            zip_name = f"chromedriver_{sys.platform}.zip"
            chrome_folder = r"C:\Program Files (x86)\Google\Chrome\Application"

            if not os.path.isdir(chrome_folder):
                if os.path.isdir(r"C:\Program Files\Google\Chrome\Application"):
                    chrome_folder = r"C:\Program Files (x86)\Google\Chrome\Application"
                else:
                    raise NotADirectoryError(f'Folder not found: {chrome_folder}')

            chrome_version = None
            for folder_name in os.listdir(chrome_folder):
                if re.match(r'[1-9].*\..*\..*\..*', folder_name):
                    chrome_version = folder_name.split('.')[0]
                    break

            if not chrome_version:
                raise ValueError(f'No Chrome version found')
        elif sys.platform == "linux":
            linux_bit = 64 if ctypes.sizeof(ctypes.c_voidp) == 8 else 32
            zip_name = f"chromedriver_{sys.platform}{linux_bit}.zip"
            chrome_version = \
                os.popen("google-chrome --version") \
                .read().lstrip("Google Chrome").split('.')[0]

        else:
            raise NotImplemented(f'Platform not supported: {sys.platform}')

    if not chrome_version:
        raise ValueError(f'Unable to get chrome version, check if chrome is installed')

    link = driver_storage_link + "/LATEST_RELEASE_" + chrome_version

    with closing(requests.get(link, stream=True)) as resp:
        version_num = (resp.content.decode("utf-8"))

    zip_file_url = driver_storage_link + "/" + version_num + "/" + zip_name
    request_f = requests.get(zip_file_url)
    zip_f = zipfile.ZipFile(io.BytesIO(request_f.content))
    zip_f.extractall()

    tmp_folder_path = os.path.join(
        os.path.dirname(os.path.abspath(file)),
        "tmp"
    )

    if not os.path.isdir(tmp_folder_path):
        os.makedirs(tmp_folder_path)

    if sys.platform == "win32":
        driver_name = "chromedriver.exe"
    else:
        driver_name = "chromedriver"

    src_driver_path = os.path.join(os.getcwd(), driver_name)
    dst_driver_path = os.path.join(tmp_folder_path, driver_name)

    shutil.move(src_driver_path, dst_driver_path)

    if sys.platform == "linux":
        os.system(f'chmod 755 {dst_driver_path}')

    return dst_driver_path


def lookup_error_version(error_message):
    result = re.search(
        r".*Current browser version is ([\d\.].*) with binary path",
        error_message
    )
    if result:
        return int(result.group(1).split(".")[0])
    else:
        return None