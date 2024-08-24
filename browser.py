import os

def get_manifest_json(id):
    return """{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Proxy_%s",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
""" % str(id)


def get_background_js(host, port, username, password):
    return """var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (host, port, username, password)


def create_proxy_folders():
    with open("proxies.txt", "r") as f:
        proxies = f.read().split("\n")

    for i in range(len(proxies)):
        os.makedirs(f"Proxies/Proxy_{i}", exist_ok=True)
        host, port, username, password = proxies[i].split(":")
        manifest_json = get_manifest_json(i)
        background_js = get_background_js(host, port, username, password)
        with open(f"Proxies/Proxy_{i}/manifest.json", "w") as f:
            f.write(manifest_json)

        with open(f"Proxies/Proxy_{i}/background.js", "w") as f:
            f.write(background_js)


import undetected_chromedriver as uc
import numpy as np
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.action_chains import ActionChains
import os


class Browser:
    def __init__(self, proxy_id=250, reset_freq=0) -> None:
        self.proxy_id = proxy_id
        self.reset_freq = reset_freq
        self.reset_browser()

    def reset_browser(self):
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.geolocation": 2
        }
        options.add_experimental_option("prefs", prefs)

        if self.proxy_id != 250:
            options.add_argument(f"--load-extension=C:\\Users\\An-Nguy3n\\Desktop\\VIS_Crawler\\Proxies\\Proxy_{self.proxy_id}")

        self.driver = uc.Chrome(options=options)
        self.actions = ActionChains(self.driver)
        self.count_done = 0
        self.browse("file:///"+os.path.abspath("blank.html").replace("\\", "/").replace("c:/", "C:/"))

    def change_proxy(self, new_proxy_id=None):
        if new_proxy_id is None:
            new_proxy_id = np.random.randint(251)

        self.proxy_id = new_proxy_id
        self.reset_browser()

    def scroll_to_bottom(self, wait_page_load=1):
        current_height = self.driver.execute_script("return document.body.scrollHeight;")
        while True:
            self.driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(wait_page_load)
            new_height = self.driver.execute_script("return document.body.scrollHeight;")
            if new_height == current_height: break
            current_height = new_height

    def browse(self, url):
        self.driver.get(url)

    def get_soup(self):
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def check_target_element(self, soup, tag_name, attrs):
        target = soup.find(tag_name, attrs)
        if target is None:
            return False

        return True

    def done(self):
        self.count_done += 1
        if self.count_done == self.reset_freq:
            self.count_done = 0
            self.proxy_id = np.random.randint(251)
            self.reset_browser()
        self.browse("file:///"+os.path.abspath("blank.html").replace("\\", "/").replace("c:/", "C:/"))

    def close(self):
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass
