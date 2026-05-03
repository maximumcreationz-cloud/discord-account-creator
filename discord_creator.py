import os
import json
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "password": "SecurePassword123!",
            "date_of_birth": "15/05/1995",  # dd/mm/yyyy
            "headless": False,
            "timeout": 15
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = self.default_config
                self.save_config()
        else:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):
        return self.config.get(key)

class DiscordAccountCreator:
    def __init__(self):
        self.config = Config()
        self.driver = self._setup_driver()

    def _setup_driver(self):
        options = Options()
        if self.config.get("headless"):
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        # Masks the 'webdriver' property to help avoid bot detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def human_type(self, element, text):
        """Types text character by character with random delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def register(self, email, username):
        try:
            self.driver.get("https://discord.com/register")
            wait = WebDriverWait(self.driver, self.config.get("timeout"))

            # Fill Basic Info
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.human_type(email_field, email)
            self.human_type(self.driver.find_element(By.NAME, "username"), username)
            self.human_type(self.driver.find_element(By.NAME, "password"), self.config.get("password"))

            # Handle Custom Dropdowns (Discord uses React-Select, not standard HTML Select)
            day, month, year = self.config.get("date_of_birth").split('/')
            month_name = datetime.strptime(month, "%m").strftime("%B")

            # Select Month
            self.driver.find_element(By.CSS_SELECTOR, "div[class*='month']").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@id, 'react-select') and text()='{month_name}']"))).click()
            
            # Select Day
            self.driver.find_element(By.CSS_SELECTOR, "div[class*='day']").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@id, 'react-select') and text()='{int(day)}']"))).click()
            
            # Select Year
            self.driver.find_element(By.CSS_SELECTOR, "div[class*='year']").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@id, 'react-select') and text()='{year}']"))).click()

            # Submit
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            print("\nForm submitted! Please solve the CAPTCHA in the browser window.")
            input("Press Enter here AFTER you have finished the CAPTCHA and see the Discord dashboard...")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    email = input("Enter Email: ")
    user = input("Enter Username: ")
    bot = DiscordAccountCreator()
    bot.register(email, user)
