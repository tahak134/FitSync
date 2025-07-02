import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

# Define constants
FRONTEND_URL = "http://localhost:5173"
DRIVER_PATH = "C:\\Users\\TahaK\\Desktop\\chromedriver-win64\\chromedriver.exe"  # Update this path to your ChromeDriver location


class TestFitSync(unittest.TestCase):
    def setUp(self):
        # Set up the WebDriver
        service = Service(DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()

    def tearDown(self):
        # Close the browser
        self.driver.quit()


    def test_user_login(self):
        """Test user login."""
        driver = self.driver
        driver.get(f"{FRONTEND_URL}/login")

        # Fill out the login form
        driver.find_element(By.NAME, "email").send_keys("tahaboss341@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("test3")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirection to the dashboard
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
        self.assertIn("dashboard", driver.current_url)

    def test_exercise_search(self):
        """Test searching for exercises."""
        driver = self.driver
        driver.get(f"{FRONTEND_URL}/exercises")

        # Perform a search
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search exercises']")
        search_input.send_keys("Push-ups")
        search_input.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "exercise-card")))
        results = driver.find_elements(By.CLASS_NAME, "exercise-card")
        self.assertGreater(len(results), 0, "No exercises found")

    def test_create_custom_routine(self):
        """Test creating a custom routine."""
        driver = self.driver
        driver.get(f"{FRONTEND_URL}/custom-routines")

        # Click the 'Add Custom Routine' button
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='Add Custom Routine']").click()

        # Fill out the routine form
        driver.find_element(By.NAME, "routineName").send_keys("Test Routine")
        driver.find_element(By.NAME, "duration").send_keys("30")
        driver.find_element(By.NAME, "difficultyLevel").send_keys("Intermediate")
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='Save Routine']").click()

        # Verify routine is listed
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "routine-card")))
        routine_card = driver.find_element(By.CLASS_NAME, "routine-card").text
        self.assertIn("Test Routine", routine_card)

    def test_daily_summary(self):
        """Test viewing the daily summary."""
        driver = self.driver
        driver.get(f"{FRONTEND_URL}/daily-diary")

        # Click on the 'View Daily Summary' button
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='View Daily Summary']").click()

        # Wait for the summary modal to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "summary-modal")))
        summary = driver.find_element(By.CLASS_NAME, "summary-modal").text
        self.assertIn("Total Calories", summary)


if __name__ == "__main__":
    unittest.main()
