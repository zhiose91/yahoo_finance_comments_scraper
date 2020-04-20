def download_driver():
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


def download_driver_AWS_linux_2():
    """Downloading chromedriver with corresponding version"""
    import requests
    import os
    import re

    chrome_version = os.popen("google-chrome --version").read()
    version_num = chrome_version.replace("Google Chrome ", "").split(".")[0]

    driver_API = "https://chromedriver.storage.googleapis.com/"
    zip_name = "chromedriver_linux64.zip"

    r = requests.get(driver_API)
    pattern = f'<Key>({version_num}\.[.\d]+)/{zip_name}</Key>'

    matched_drivers = re.findall(pattern, r.text)

    if matched_drivers:
        print(f'Latest driver found: {matched_drivers[-1]}')

    driver_url = f'{driver_API}{matched_drivers[-1]}/{zip_name}'
    print(f'Downloading Driver: {driver_url}')
    os.system(f'sudo wget {driver_url}')
    os.system(f'sudo unzip {zip_name}')
    os.system(f'sudo mv chromedriver /usr/bin/chromedriver')
