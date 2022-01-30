from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from pathlib import Path

FIRST_DAY = datetime.datetime.strptime("Jan 24 2022", "%b %d %Y")
CONFIG_FILE = Path.home() / Path(".edu-login")


class Edupage(Chrome):
    is_in = False
    week = 1

    def __init__(self):
        super().__init__(ChromeDriverManager().install())

    def start(self, username, password):
        self.username = username
        self.password = password
        self.get("https://ufaz.edupage.org/")

    def login(self):
        self.find_element("name", "username").send_keys(self.username)
        self.find_element("name", "password").send_keys(self.password)
        self.find_element("class name", "skgdFormSubmit").click()
        self.is_in = True

    def timetable(self):
        if not self.is_in:
            self.login()
        self.get("https://ufaz.edupage.org/dashboard/eb.php?mode=timetable")

    def next_week(self):
        if self.week != 16:
            WebDriverWait(self, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[1]/span[5]/span[2]")
                )
            ).click()
            self.week += 1

    def previous_week(self):
        if self.week != 1:
            WebDriverWait(self, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[1]/span[5]/span[1]")
                )
            ).click()
            self.week -= 1


def read_conf():
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open(mode="r") as f:
                config = {}
                for line in f.readlines():
                    temp = line.split("=")
                    config[temp[0]] = temp[1][:-1]
            return config
        except Exception as e:
            print(e)
            return None
    return None


def write_conf(config: dict):
    with CONFIG_FILE.open(mode="w") as f:
        for key, value in config.items():
            print(f"{key}={value}", file=f)


def main():
    d = Edupage()
    if config := read_conf():
        print("Configuration file detected, trying to login from there")
        username = config["username"]
        password = config["password"]
    else:
        print("Please, enter login and password to be used in login process")
        username = input("Username: ")
        password = input("Password: ")
        write_conf({"username": username, "password": password})
    d.start(username, password)
    d.login()
    d.timetable()
    for i in range(6):
        d.next_week()
        time.sleep(1)
    print(f"Went 6 weeks forward, but actually on week {d.week}")
    time.sleep(3)
    for i in range(5):
        d.previous_week()
        time.sleep(1)
    print(f"Went 5 weeks backwards, but actually on week {d.week}")
    time.sleep(3)
    input("quit")
    d.quit()


if __name__ == '__main__':
    main()
