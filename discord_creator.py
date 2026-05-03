import os
import json
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "password": "SecurePassword123!",
            "date_of_birth": "01/01/1990",
            "headless": False,
            "timeout": 10,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.config = self.default_config
                self.save_config()
        else:
            self.config = self.default_config
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def get_random_user_agent(self):
        user_agents = self.get("user_agents", [])
        return random.choice(user_agents) if user_agents else self.default_config["user_agents"][0]

class UserInputValidator:
    @staticmethod
    def validate_email(email):
        if not email:
            raise ValueError('Please enter an email')
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError('Please enter a valid email address')
        return email
    
    @staticmethod
    def validate_username(username):
        if not username:
            raise ValueError('Please enter a username')
        if len(username) < 2 or len(username) > 32:
            raise ValueError('Username must be between 2 and 32 characters')
        return username
    
    @staticmethod
    def validate_password(password, default_password):
        if not password:
            return default_password
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password
    
    @staticmethod
    def validate_date_of_birth(date_of_birth, default_dob):
        if not date_of_birth:
            return default_dob
        
        try:
            # Parse date in different formats
            if '/' in date_of_birth:
                parts = date_of_birth.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                elif len(parts) == 2:
                    month, year = parts
                    day = "01"
                else:
                    raise ValueError('Invalid date format')
            else:
                raise ValueError('Please use the format dd/mm/yyyy')
            
            # Convert to integers
            day = int(day)
            month = int(month)
            year = int(year)
            
            # Validate ranges
            if day < 1 or day > 31:
                raise ValueError("Day must be between 1 and 31")
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
            current_year = datetime.now().year
            if year < 1950 or year > current_year - 13:
                raise ValueError("You must be at least 13 years old to use Discord")
            
            # Return in the format Discord expects
            return f"{day:02d}/{month:02d}/{year}"
        except ValueError as e:
            raise ValueError(f'Invalid date format: {str(e)}')

class DiscordAccountCreator:
    def __init__(self, headless=False):
        self.config = Config()
        self.timeout = self.config.get("timeout", 10)
        self.driver = self._setup_driver(headless)
    
    def _setup_driver(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={self.config.get_random_user_agent()}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver: {str(e)}")
    
    def human_type(self, element, text):
        """Type text like a human with random delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def register_account(self, email, username, password, date_of_birth):
        try:
            # Navigate to registration page
            self.driver.get("https://discord.com/register")
            
            # Wait for email field to be present
            email_field = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            
            # Parse date of birth
            day, month, year = date_of_birth.split('/')
            
            # Fill out the form with human-like typing
            self.human_type(email_field, email)
            
            # Tab to username field and type
            email_field.send_keys(Keys.TAB)
            username_field = self.driver.switch_to.active_element
            self.human_type(username_field, username)
            
            # Tab to password field and type
            username_field.send_keys(Keys.TAB)
            password_field = self.driver.switch_to.active_element
            self.human_type(password_field, password)
            
            # Handle date of birth dropdowns
            password_field.send_keys(Keys.TAB)  # Move to month dropdown
            month_dropdown = self.driver.switch_to.active_element
            month_select = Select(month_dropdown)
            month_select.select_by_visible_text(month)
            
            month_dropdown.send_keys(Keys.TAB)  # Move to day dropdown
            day_dropdown = self.driver.switch_to.active_element
            day_select = Select(day_dropdown)
            day_select.select_by_visible_text(day)
            
            day_dropdown.send_keys(Keys.TAB)  # Move to year dropdown
            year_dropdown = self.driver.switch_to.active_element
            year_select = Select(year_dropdown)
            year_select.select_by_visible_text(year)
            
            # Take a screenshot for debugging
            self.driver.save_screenshot("filled_form.png")
            
            # Check for CAPTCHA
            try:
                captcha_frame = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title*='reCAPTCHA']"))
                )
                print("CAPTCHA detected! Please solve it manually in the browser.")
                input("Press Enter after solving CAPTCHA...")
            except TimeoutException:
                print("No CAPTCHA detected or CAPTCHA loading timed out.")
            
            # Submit the form
            try:
                # Find and click the continue button
                continue_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                continue_button.click()
                print("Registration form submitted successfully!")
                
                # Wait for potential next steps
                time.sleep(3)
                
                # Check if verification is needed
                try:
                    verify_text = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'verify')]"))
                    )
                    print("Email verification required. Please check your
