import os
import winreg
import pystray
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

app_name = "Router Settings"

def router_controller(task="dashboard", headless=False):
    icon.icon = imageActive
    # Initialize web driver
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    if headless:
        options.add_argument('--headless')
    else:
        options.add_argument("--app=http://192.168.1.1/login.cgi")
        options.add_argument("--window-size=1248,768")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to login page
        driver.get("http://192.168.1.1/login.cgi")

        # Locate username and password fields and enter login credentials
        wait = WebDriverWait(driver, 10)
        username = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        password = wait.until(EC.visibility_of_element_located((By.ID, "userpassword")))
        username.send_keys("user")
        password.send_keys("LTE@Endusr")

        # Locate and click the login button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Login']")))
        login_button.click()
        if(task == "reboot"):
            # locate the maintenance element and hover over it
            maintenance_element = driver.find_element(By.ID, "MT")
            actions = ActionChains(driver)
            actions.move_to_element(maintenance_element).perform()

            # locate the reboot link and click on it
            reboot_link = driver.find_element(By.XPATH, "//a[contains(text(),'Reboot')]")
            reboot_link.click()
            # Confirm reboot
            wait.until(EC.frame_to_be_available_and_switch_to_it("mainFrame"))
            # locate the reboot button and click on it
            reboot_button = driver.find_element(By.NAME, "sysSubmit")
            reboot_button.click()

            # switch back to the main frame
            driver.switch_to.default_content()

            ok_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[text()="OK"]')))
            ok_button.click()
        if (headless == False):
            print('done')
            current_handles = driver.window_handles
            WebDriverWait(driver, 60*60).until(lambda d: current_handles != d.window_handles) # wait for 1 hour
        driver.quit()
        icon.icon = image
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        icon.icon = image

def on_quit():
    icon.stop()


def get_startup_status():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
    try:
        value = winreg.QueryValueEx(key, app_name)[0]
        return True
    except:
        return False

def startup_toggle(icon, item):
    global startup_status
    startup_status = not item.checked
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
    if startup_status:
        value = os.path.join(os.getcwd(), "router_settings.exe")
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, value)
    else:
        winreg.DeleteValue(key, app_name)

startup_status = get_startup_status()

image = Image.open('E:/NdmGjr/router_settings/icon.png')
imageActive = Image.open('E:/NdmGjr/router_settings/icon-active.png')
icon = pystray.Icon(app_name, image, app_name)
icon.menu = pystray.Menu(
    pystray.MenuItem(text="Dashboard", action=lambda: router_controller("dashboard"), default=True),
    pystray.MenuItem("Reboot", lambda: router_controller("reboot")),
    pystray.MenuItem("Reboot Headless", lambda: router_controller("reboot", True)),
    pystray.MenuItem("Quit", on_quit),
    pystray.MenuItem("Run at startup", startup_toggle, checked=lambda item: startup_status)
)
icon.run()

# pyinstaller --name router_settings main.py --icon=icon-active.png --noconsole --onefile
