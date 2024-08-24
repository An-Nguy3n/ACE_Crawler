from browser import Browser
import time
import numpy as np
from colorama import Fore, Style
import re
import os
import json
import threading
from selenium.webdriver.common.by import By



RED = Fore.LIGHTRED_EX
GREEN = Fore.LIGHTGREEN_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
YELLOW = Fore.LIGHTYELLOW_EX
RESET = Style.RESET_ALL


def move_and_click_spec(br: Browser):
    try:
        br.actions.move_to_element(br.driver.find_element(By.ID, "specifications")).perform()
    except: pass
    try:
        for button in br.driver.find_elements(By.ID, "show-more-btn"):
            if button.get_attribute("aria-label") == "Open Specifications section": button.click()
    except: pass
    time.sleep(1)


def check_spec(br: Browser):
    soup = br.get_soup()
    check = br.check_target_element(soup, "div", {"id": "specifications"})
    a = time.time()
    while not check:
        br.scroll_to_bottom()
        move_and_click_spec(br)
        soup = br.get_soup()
        check = br.check_target_element(soup, "div", {"id": "specifications"})
        if time.time() - a >= 100.0:
            break

    return check


def get_data(br: Browser,
             href: str,
             id: int,
             lock: threading.Lock):
    br.browse(href)
    br.scroll_to_bottom()

    move_and_click_spec(br)
    check = check_spec(br)

    for i in range(1000):
        if check: break

        print(MAGENTA, str(id)+RESET, end=" ", flush=True)
        br.done()

        br.browse(href)
        br.scroll_to_bottom()

        move_and_click_spec(br)
        check = check_spec(br)

    if not check: return None

    data = {}
    soup = br.get_soup()

    product_info = soup.find("div", attrs={"class":"product-info"})
    sku = "_" + re.search(r'"sku": "(.*?)"', str(soup)).group().replace('"sku": "', "").replace('"', "")
    upc = "_" + re.search(r'"gtin": "(.*?)"', str(soup)).group().replace('"gtin": "', "").replace('"', "")
    name = product_info.find("h1").text
    price = soup.find("div", attrs={"class": "price"}).text

    data["_sku"] = sku
    data["_upc"] = upc
    data["_name"] = name
    data["_price"] = price

    for li in soup.find("div", {"id": "specifications"}).find_all("li"):
        if not li.text.startswith("Click here to"):
            temp = li.text.split(":")
            data[temp[0]] = ":".join(temp[1:])

    data["Product_URL"] = href
    br.done()
    return data


def get_data_thread(br: Browser):
    global current_index
    global lock
    global num_href
    global list_href

    while True:
        lock.acquire()
        index = current_index[0]
        current_index[0] += 1
        lock.release()

        if index >= num_href: break
        if os.path.exists(f"Data\\{index}.json"):
            print(YELLOW, f"Data\\{index}.json"+RESET, end="\n", flush=True)
            continue

        href = list_href[index]
        try:
            data = get_data(br, href, index, lock)
            if data is None: raise

            with open(f"Data\\{index}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(GREEN, str(index)+RESET, end=" ", flush=True)
        except Exception as ex:
            print(ex)
            print(RED, str(index)+RESET, end=" ", flush=True)


if __name__ == "__main__":
    with open("Ace_hrefs.txt", "r") as f:
        list_href = f.read().split("\n")

    num_href = len(list_href)

    current_index = [0]
    lock = threading.Lock()

    list_br = [Browser(250) for _ in range(8)]

    threads = []
    for _ in range(8):
        thread = threading.Thread(target=get_data_thread, args=(list_br[_],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for br in list_br:
        br.close()
