def win_download_driver():
    """Downloading chromedriver.exe with corresponding version"""
    import requests
    from contextlib import closing
    import zipfile
    import re
    import os
    import io

    print("Initialize downloading driver:", end = " ")
    driver_API = "https://chromedriver.storage.googleapis.com"
    zip_name = "chromedriver_win32.zip"
    chrome_folder = r"C:\Program Files (x86)\Google\Chrome\Application"

    for folder in os.listdir(chrome_folder):
        if re.match(r'[1-9].*\..*\..*\..*', folder):
            chrome_version = folder.split('.')[0]
            print(f"version [{chrome_version}]")
            break
    link = driver_API + "/LATEST_RELEASE_" + chrome_version

    with closing(requests.get(link, stream=True)) as resp:
        version_num = (resp.content.decode("utf-8"))

    zip_file_url = driver_API + "/" + version_num + "/" + zip_name
    request_f = requests.get(zip_file_url)
    zip_f = zipfile.ZipFile(io.BytesIO(request_f.content))
    zip_f.extractall()
    print("Download completed")
