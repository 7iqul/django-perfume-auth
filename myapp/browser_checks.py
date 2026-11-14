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

        perfume = Perfume.objects.create(
            name='Cedar', brand='Ambre', price='120.00', size_ml=50
        )
        get_user_model().objects.create_user(
            username='browser_customer', password='Browser-test-pass-72!'
        )

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1280,900')
        if os.environ.get('CHROME_BINARY'):
            options.binary_location = os.environ['CHROME_BINARY']
        service = Service(executable_path=os.environ.get('CHROMEDRIVER'))
        browser = webdriver.Chrome(options=options, service=service)
        self.addCleanup(browser.quit)

        browser.get(self.live_server_url + reverse('login'))
        browser.find_element(By.NAME, 'username').send_keys('browser_customer')
        browser.find_element(By.NAME, 'password').send_keys('Browser-test-pass-72!')
        browser.find_element(By.CSS_SELECTOR, 'form.auth button').click()

        browser.get(self.live_server_url + reverse('detail', args=[perfume.pk]))
        browser.find_element(By.CSS_SELECTOR, 'main form button').click()
        browser.get(self.live_server_url + reverse('cart'))
        self.assertIn('Cedar', browser.find_element(By.CSS_SELECTOR, '.item').text)
        self.assertIn('120.00 SAR', browser.find_element(By.CSS_SELECTOR, '.total').text)
        browser.find_element(By.CSS_SELECTOR, '.item button').click()
        self.assertIn('Your cart is empty', browser.find_element(By.TAG_NAME, 'main').text)
