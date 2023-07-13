import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pyvirtualdisplay import Display
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def thinking():
    time.sleep(random.uniform(0.5, 3))

def get_token(username, password):
    # This fails more often than not but it seems to work eventually.
    # I know that we can do better by using voice recognition but I
    # would prefer to avoid abusing an accessibility feature.
    print('Getting a new token, this can take a while...')
    auth_cookie = None
    while not auth_cookie:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
                options=options,
            )

            try:
                driver.get('https://www.usmobile.com/?ln=true')
                driver.get_screenshot_as_file("snap-initial.png")
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))
                thinking()
                driver.find_element(By.NAME, 'username').send_keys(username)
                thinking()
                driver.find_element(By.NAME, 'password').send_keys(password)
                thinking()
                button = next(b for b in driver.find_elements(By.TAG_NAME, 'button') if 'SIGN IN' in b.text)
                # Click on a random spot, not too close to the edge
                x = random.randint(5, button.size['width'] - 10)
                y = random.randint(5, button.size['height'] - 10)
                ac = ActionChains(driver)
                driver.get_screenshot_as_file("snap-request.png")
                ac.move_to_element_with_offset(button, x, y).click().perform()
                time.sleep(5)
                driver.get_screenshot_as_file("snap-response.png")
                try:
                    auth_cookie = next(c for c in driver.get_cookies() if c['name'] == '@usm-auth/token')
                except StopIteration:
                    # Most often this means we got a challenge page, try again...
                    print(f'Failed to get token - retrying...')
            finally:
                driver.quit()
        finally:
            display.stop()
    # Truly a cause for celebration!
    print(f"Got a new token!")
    return auth_cookie['value']
