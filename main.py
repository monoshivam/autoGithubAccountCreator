import time
import random
import string
import json
import requests
import undetected_geckodriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import re
from pynput.mouse import Controller
import screeninfo
import threading
import os
from pynput import mouse as ms

#Login for ending the script with middle mouse button click
def on_click(x, y, button, pressed):
    global stop_flag
    if pressed and button == ms.Button.middle:
        print("Middle mouse button clicked! Exiting...")
        os._exit(0)
def listen_for_middle_click():
    with ms.Listener(on_click=on_click) as listener:
        listener.join()

created_count = 0

mouse = Controller()
screen = screeninfo.get_monitors()[0]
width, height = screen.width, screen.height
threshold = 10

class GitHubAutoSignup:
    def __init__(self):
        self.password = "Testpass@123"
        self.driver = None
        self.wait = None
        self.temp_email = None
        self.temp_password = None
        self.username = None
        self.accounts_file = "github_accounts.txt"

    def setup_firefox_driver(self):
        """Setup undetected Firefox driver with stealth options"""
        # Initialize Firefox driver with no parameters

        options = Options()
        options.add_argument("-private")

        self.driver = uc.Firefox(options=options)

        # Set additional stealth properties
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        self.driver.execute_script("window.chrome = { runtime: {} }")

        # Random viewport size to look more human
        viewport_width = random.randint(1200, 1920)
        viewport_height = random.randint(800, 1080)
        self.driver.set_window_size(viewport_width, viewport_height)

        self.wait = WebDriverWait(self.driver, 30)


    def human_like_delay(self, min_delay=1, max_delay=3):
        """Add human-like random delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def human_like_typing(self, element, text, delay_range=(0.05, 0.15)):
        """Type text with human-like delays between keystrokes"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))

    def generate_random_username(self, length=8):
        """Generate random username"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"user{username}"

    def create_temp_email(self):
        """Create temporary email using mail.tm API"""
        try:
            # Get available domains
            domains_response = requests.get("https://api.mail.tm/domains")
            domains = domains_response.json()["hydra:member"]
            domain = domains[0]["domain"]

            # Generate random email
            email_local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"{email_local}@{domain}"

            # Create account
            account_data = {
                "address": email,
                "password": "temppassword123"
            }

            create_response = requests.post("https://api.mail.tm/accounts", json=account_data)

            if create_response.status_code == 201:
                self.temp_email = email
                self.temp_password = "temppassword123"
                print(f"Created temporary email: {email}")
                return True
            else:
                print(f"Failed to create email: {create_response.text}")
                return False

        except Exception as e:
            print(f"Error creating temp email: {e}")
            return False

    def get_email_token(self):
        """Get authentication token for email access"""
        try:
            auth_data = {
                "address": self.temp_email,
                "password": self.temp_password
            }

            response = requests.post("https://api.mail.tm/token", json=auth_data)
            if response.status_code == 200:
                return response.json()["token"]
            return None
        except Exception as e:
            print(f"Error getting email token: {e}")
            return None

    def get_verification_code_from_email(self, token):
        """Get verification code from GitHub email"""
        headers = {"Authorization": f"Bearer {token}"}

        # Wait for email to arrive
        for attempt in range(30):  # Wait up to 5 minutes
            try:
                response = requests.get("https://api.mail.tm/messages", headers=headers)
                if response.status_code == 200:
                    messages = response.json()["hydra:member"]

                    for message in messages:
                        if "github" in message["subject"].lower() or "verification" in message["subject"].lower():
                            # Get message content
                            msg_response = requests.get(f"https://api.mail.tm/messages/{message['id']}", headers=headers)
                            if msg_response.status_code == 200:
                                content = msg_response.json()["text"]

                                # Extract verification code (6-digit number)
                                code_match = re.search(r'\b\d{8}\b', content)
                                if code_match:
                                    return code_match.group()

                print(f"Waiting for email... attempt {attempt + 1}/30")
                time.sleep(10)

            except Exception as e:
                print(f"Error checking emails: {e}")
                time.sleep(10)

        return None

    def navigate_to_github_signup(self):
        """Navigate to GitHub signup page with human-like behavior"""

        # Then navigate to signup
        self.driver.get("https://github.com/join")
        self.human_like_delay(1, 2)

    def fill_signup_form(self):
        """Fill GitHub signup form"""
        try:
            # Generate username
            self.username = self.generate_random_username()

            # Fill email with human-like typing
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            self.human_like_typing(email_field, self.temp_email)
            self.human_like_delay(1, 2)

            # Fill password with human-like typing
            password_field = self.driver.find_element(By.ID, "password")
            self.human_like_typing(password_field, self.password)
            self.human_like_delay(1, 2)

            # Fill username with human-like typing
            username_field = self.driver.find_element(By.ID, "login")
            self.human_like_typing(username_field, self.username)

            self.human_like_delay(3, 4)

            # Click continue/signup button with human-like behavior
            continue_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'Button--primary') or @type='submit']")
            self.driver.execute_script("arguments[0].click();", continue_button)

            return True

        except Exception as e:
            print(f"Error filling signup form: {e}")
            return False

    def handle_email_already_exists(self):
        """Handle case where email already exists"""
        try:
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'already taken') or contains(text(), 'already exists')]")
            if error_elements:
                print("Email already exists, creating new temp email...")
                if self.create_temp_email():
                    return self.fill_signup_form()
            return True
        except:
            return True

    def wait_for_manual_puzzle_completion(self):
        """Wait for user to manually complete the visual puzzle"""
        print("\n" + "="*50)
        print("MANUAL ACTION REQUIRED!")
        print("Please complete the visual puzzle in the browser.")
        print("Once you reach the 'Enter code sent to your email' screen,")
        print("Bring your mouse to bottom right of the screen to continue...")
        print("="*50)

        while True:
            x, y = mouse.position
            if x >= width - threshold and y >= height - threshold:
                print("Mouse reached the bottom-right corner of the screen!")
                break

        # Wait a moment for page to load
        time.sleep(3)

    def enter_verification_code(self):
        """Get verification code from email and enter it"""
        print("Getting verification code from email...")

        token = self.get_email_token()
        if not token:
            print("Failed to get email token")
            return False

        verification_code = self.get_verification_code_from_email(token)
        if not verification_code:
            print("Failed to get verification code from email")
            return False

        print(f"Found verification code: {verification_code}")

        # Enter verification code with human-like behavior
        try:
            code_field0 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-0")
            ))
            code_field0.send_keys(verification_code[0])

            code_field1 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-1")
            ))
            code_field1.send_keys(verification_code[1])

            code_field2 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-2")
            ))
            code_field2.send_keys(verification_code[2])

            code_field3 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-3")
            ))
            code_field3.send_keys(verification_code[3])

            code_field4 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-4")
            ))
            code_field4.send_keys(verification_code[4])

            code_field5 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-5")
            ))
            code_field5.send_keys(verification_code[5])

            code_field6 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-6")
            ))
            code_field6.send_keys(verification_code[6])

            code_field7 = self.wait.until(EC.presence_of_element_located(
                (By.ID, "launch-code-7")
            ))
            code_field7.send_keys(verification_code[7])

            self.human_like_delay(2, 2)
            return True

        except Exception as e:
            print(f"Error entering verification code: {e}")
            return False

    def sign_in_with_github(self):
        """Completing Signing in"""
        try:

            # Fill in sign up form
            self.driver.find_element(By.ID, "login_field").send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.human_like_delay(1, 2)

            # Look for sign in button
            sign_in_button = self.driver.find_element(By.XPATH, "//input[@type='submit' or contains(@class, 'btn-primary')]")
            self.driver.execute_script("arguments[0].click();", sign_in_button)
            # sign_in_button.click()
            self.human_like_delay(2, 3)
            return True

        except Exception as e:
            print(f"Error completing signin: {e}")
            return False

    def save_account_details(self):
        """Save account details to file"""
        account_info = {
            "email": self.temp_email,
            "username": self.username,
            "password": self.password,
            "temp_email_password": self.temp_password,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(self.accounts_file, "a") as f:
            f.write(json.dumps(account_info) + "\n")

        print(f"Account details saved: {self.username} - {self.temp_email}")

    def create_single_account(self):
        """Create a single GitHub account"""
        print(f"\n{'='*60}")
        print("Starting new GitHub account creation...")
        print(f"{'='*60}")
        global created_count

        # Setup new browser instance
        if created_count > 0:
            self.driver.quit()

        self.setup_firefox_driver()

        try:
            # Step 1: Create temporary email
            self.navigate_to_github_signup()

            if not self.create_temp_email():
                print("Failed to create temporary email")
                return False

            # Step 2: Fill signup form
            if not self.fill_signup_form():
                print("Failed to fill signup form")
                return False

            # Step 3: Handle email already exists
            if not self.handle_email_already_exists():
                print("Failed to handle email conflict")
                return False

            # Step 4: Wait for manual puzzle completion
            self.wait_for_manual_puzzle_completion()

            # Step 5: Enter verification code
            if not self.enter_verification_code():
                print("Failed to enter verification code")
                return False

            # Step 6: Sign in with GitHub
            if not self.sign_in_with_github():
                print("Failed to sign in with GitHub")
                return False

            # Step 7: Save account details
            self.save_account_details()

            print(f"✅ Successfully created account: {self.username}")
            return True

        except Exception as e:
            print(f"Error creating account: {e}")
            return False

    def run_continuous_creation(self, num_accounts=None):
        """Run continuous account creation"""
        global created_count

        try:
            while True:
                if num_accounts and created_count >= num_accounts:
                    break

                success = self.create_single_account()
                if success:
                    created_count += 1

                print(f"\nAccounts created so far: {created_count}")

        except KeyboardInterrupt:
            print(f"\nStopped by user. Total accounts created: {created_count}")
        finally:
            print("DONEEEEEEEEEEEEEEEEEEE!!!")

def main():
    creator = GitHubAutoSignup()

    print("GitHub Account Auto-Creator")
    print("This script will create GitHub accounts using temporary emails from mail.tm")
    print("\nPress Ctrl+C to stop the script at any time")

    try:
        num_accounts = input("\nHow many accounts to create? (Press Enter for unlimited): ").strip()
        num_accounts = int(num_accounts) if num_accounts else None
    except:
        num_accounts = None

    creator.run_continuous_creation(num_accounts)

if __name__ == "__main__":
    listener_thread = threading.Thread(target=listen_for_middle_click, daemon=True)
    listener_thread.start()
    main()
