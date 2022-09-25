# Justin Martinez
# AutoChromedriver module


import os
import platform
import shutil
import subprocess
import sys
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (SessionNotCreatedException,
                                        WebDriverException)
from selenium.webdriver.chrome.options import Options


class AutoChromedriver:
    def __init__(self, verbose=False, chromedriver_path=None) -> None:
        # Test chromedriver out in Path to see if a session can be started
        try:
            options = Options()
            options.add_argument("--headless")
            if chromedriver_path is None:
                driver = webdriver.Chrome(options=options)
            else:
                assert os.path.exists(
                    chromedriver_path
                ), "Unable to locate supplied path to chromedriver executable"
                driver = webdriver.Chrome(
                    executable_path=chromedriver_path, options=options
                )
            driver.close()

        except WebDriverException as e:
            print("Encountered", e)

            # Checks for chromedriver executable depending on platform
            self.os = platform.system()

            self.chromedriver_found = self.check_PATH()
            if self.chromedriver_found is None:
                self.install_dir = os.path.join(os.getcwd(), "chromedriver")
                inp = input(
                    f"Seems like chromedriver is missing or not in PATH, would you like to install it here?\n{self.install_dir} (y/n)"
                )

                # Validates input
                if inp.lower() != "y" and inp.lower() != "n":
                    sys.exit("Invalid input, exiting...")
                if inp.lower() == "n":
                    sys.exit("No install requested, exiting...")

                # Ensure the folder exists and then download/update chromedriver depending on platform
                if os.path.exists(self.install_dir) == False:
                    os.mkdir("chromedriver")
            else:
                self.install_dir = self.chromedriver_found

            if self.os == "Windows":
                self.get_chrome_version_windows()
            elif self.os == "Mac":
                self.get_chrome_version_mac()
            elif self.os == "Linux":
                self.get_chrome_version_linux()

            self.download_chromedriver()
            chromedriver_path = chromedriver_path = os.path.join(
                os.getcwd(), "chromedriver"
            )
            self.update_chromedriver()

        except SessionNotCreatedException as e:
            print("Encountered", e)
            print("Chromedriver update required, updating...")
            self.update()

    def check_PATH(self):
        # Checks PATH for chromedriver executable
        # Probably not a good way to check but it's fast enough :)
        variables = dict(os.environ)
        paths = variables["PATH"]
        paths = paths.split(";")

        executables = {
            "Windows": "chromedriver.exe",
            "Mac": "chromedriver",
            "Linux": "chromedriver",
        }
        target_executable = executables[self.os]

        for path in paths:
            if os.path.exists(path):
                files = os.listdir(path)
            for file in files:
                if file == target_executable:
                    return path

    def download_chromedriver(self):
        response = requests.get("https://chromedriver.chromium.org/downloads")
        content = BeautifulSoup(response.content, "html.parser")
        base = "https://chromedriver.storage.googleapis.com/"

        # Checking the version to download exists and is clickable
        links = [link for link in content.select(f'a[href^="{base}index.html?path="]')]
        chromedriver_version_exists = False
        for element in links:
            if element.text.split(" ")[1] == self.version:
                print("Found matching chromedriver version")
                chromedriver_version_exists = True
                break
        if chromedriver_version_exists == False:
            sys.exit("unable to find matching chromedriver version, exiting. . .")

        if self.os == "Windows":
            update_link = f"{base}{self.version}/chromedriver_win32.zip"
        if self.os == "Darwin":
            if platform.machine() == "arm":
                update_link = f"{base}{self.version}/chromedriver_mac64_m1.zip"
            else:
                update_link = f"{base}{self.version}/chromedriver_mac64.zip"
        elif self.os == "Linux":
            update_link = f"{base}{self.version}/chromedriver_linux64.zip"

        try:
            t = time.time()
            self.update_file = update_link.split("/")[-1]
            with requests.get(update_link, stream=True) as response:
                response.raise_for_status()
                with open(self.update_file, "wb") as file_download:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        file_download.write(chunk)
            print(f"Finished downloading in {round((time.time() -t), 4)}s")
            assert os.path.exists(self.update_file)
        except:
            sys.exit("error occurred while downloading file, exiting . . .")

    def get_chrome_version_windows(self):
        # Verify chrome version in local machine first
        # Windows
        if os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"):
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
                shell=True,
            )
            version = output.decode("utf-8").strip()
            self.version = version.split("=")[1]
        else:
            sys.exit("Couldn't locate Google Chrome on this machine.")

    def get_chrome_version_mac(self):
        # Running an "ls" command to Google Chrome's path
        # Mac (M1/Intel)
        if os.path.exists(
            "/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/versions/"
        ):
            version_dir = subprocess.run(
                [
                    "ls",
                    "/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/versions/",
                ],
                stdout=subprocess.PIPE,
            )
            version_dir = version_dir.stdout.decode("utf-8")
            self.version = [i for i in version_dir.split("\n") if "." in i][1]
        else:
            sys.exit("Couldn't locate Google Chrome on this machine.")

    def get_chrome_version_linux(self):
        # First check for google chrome path in /usr/bin for debian-based distros
        # If not found, check path for default AUR path for arch-based distros
        if os.path.exists("/usr/bin/google-chrome"):
            version = subprocess.run(["/usr/bin/google-chrome", "--version"])
            version = version.decode("utf-8")
            self.version = version.split(" ")[1].split(".")[1]

        elif os.path.exists("/opt/google/chrome/chrome"):
            version = subprocess.run(["/opt/google/chrome/chrome", "--version"])
            version = version.decode("utf-8")
            self.version = version.split(" ")[1].split(".")[1]

        else:
            sys.exit(
                "Couldn't find Google Chrome in the default Debian or Arch based distro paths."
            )

    def update_chromedriver(self):
        # Verify that the chromedriver zip is in the directory
        if not os.path.exists(self.update_file):
            sys.exit(
                "Looks like the chromedriver updatefile isn't in our directory. Exiting. . ."
            )
        else:
            if os.path.exists(self.install_dir):
                shutil.unpack_archive(self.update_file, self.install_dir)
                # Add the update to PATH if chromedriver was npt in PATH previously
                if self.chromedriver_found is None:
                    os.environ["PATH"] += os.pathsep + os.getcwd()