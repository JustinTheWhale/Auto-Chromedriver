import os
import requests
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException
import subprocess


class Check_chromedriver:
    def __init__(self) -> None:
        print("Checking if chromedriver needs an update. . .")
        if os.path.exists('/usr/local/bin/chromedriver'):
            try:
                options = Options()
                options.add_argument("--headless")
                driver_test = webdriver.Chrome(options=options)
                driver_test.close()
                self.update = False
                print("No update needed, starting AmexRec now")
            except SessionNotCreatedException:
                try:
                    self.update_via_bs4()
                except:
                    print("unable to update chromedriver, exiting. . .")
                    sys.exit()
        else:
            print("Chromedriver is missing for some reason, reinstalling.")
            self.update_via_bs4()

    def update_via_bs4(self):
        self.update = False
        #Running an "ls" command to Google Chrome's path since Selenium is unavalilable 
        chrome_version_dir = subprocess.run(['ls', '/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/versions/'], stdout=subprocess.PIPE)
        chrome_version_dir = chrome_version_dir.stdout.decode('utf-8')
        chrome_version = [i for i in chrome_version_dir.split('\n') if '.' in i][1]

        response = requests.get("https://chromedriver.chromium.org/downloads")
        content = BeautifulSoup(response.content, 'html.parser')
        base = 'https://chromedriver.storage.googleapis.com/'

        #Checking the version to download exists and is clickable
        links = [link for link in content.select(f'a[href^="{base}index.html?path="]')]
        chromedriver_version_exists = False
        for element in links:
            if element.text.split(' ')[1] == chrome_version:
                print("Found matching chromedriver version")
                chromedriver_version_exists = True
                break
        if chromedriver_version_exists == False:
                sys.exit("unable to find matching chromedriver version, exiting. . .")
        
        update_link = f'{base}{chrome_version}/chromedriver_mac64_m1.zip'
        try:
            t = time.time()
            with requests.get(update_link, stream=True) as response:
                response.raise_for_status()
                with open('chromedriver_mac64_m1.zip', 'wb') as file_download:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        file_download.write(chunk)
            print(f'Finished downloading in {time.time() -t}s')
            assert(os.path.exists('chromedriver_mac64_m1.zip'))
            self.update = True
        except:
            sys.exit("error occurred while downloading file, exiting . . .")