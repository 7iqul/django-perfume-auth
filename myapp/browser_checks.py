import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from .models import Perfume


class CartBrowserTest(StaticLiveServerTestCase):
    def test_customer_can_add_and_remove_a_perfume(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as expected
        from selenium.webdriver.support.ui import WebDriverWait

        perfume = Perfume.objects.create(
            name='Cedar', brand='Ambre', price='120.00', size_ml=50
        )
        get_user_model().objects.create_user(
            username='browser_customer', password='Browser-test-pass-72!'
        )

        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument('--headless')
        options.add_argument('--window-size=1280,900')
        if os.environ.get('CHROME_BINARY'):
            options.binary_location = os.environ['CHROME_BINARY']
        service = Service(executable_path=os.environ.get('CHROMEDRIVER'))
        browser = webdriver.Chrome(options=options, service=service)
        self.addCleanup(browser.quit)
        browser.set_page_load_timeout(30)
        wait = WebDriverWait(browser, 15)

        browser.get(self.live_server_url + reverse('login'))
        browser.find_element(By.NAME, 'username').send_keys('browser_customer')
        browser.find_element(By.NAME, 'password').send_keys('Browser-test-pass-72!')
        browser.find_element(By.CSS_SELECTOR, 'form.auth button').click()
        wait.until(expected.url_to_be(self.live_server_url + reverse('home')))

        browser.get(self.live_server_url + reverse('detail', args=[perfume.pk]))
        browser.find_element(By.CSS_SELECTOR, 'main form button').click()
        cart_link = (By.CSS_SELECTOR, f"a[href='{reverse('cart')}']")
        wait.until(expected.text_to_be_present_in_element(
            (By.CSS_SELECTOR, f"{cart_link[1]} .badge"), '1'
        ))
        browser.find_element(*cart_link).click()
        wait.until(expected.url_to_be(self.live_server_url + reverse('cart')))
        self.assertIn('Cedar', browser.find_element(By.CSS_SELECTOR, '.item').text)
        self.assertIn('120.00 SAR', browser.find_element(By.CSS_SELECTOR, '.total').text)
        browser.find_element(By.CSS_SELECTOR, '.item button').click()
        wait.until(expected.text_to_be_present_in_element((By.TAG_NAME, 'main'), 'Your cart is empty'))
