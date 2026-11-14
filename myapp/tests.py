from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Perfume


class StoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.perfume = Perfume.objects.create(
            name='Cedar', brand='Ambre', price='120.00', size_ml=50
        )
        cls.customer = get_user_model().objects.create_user(username='customer')
        cls.staff = get_user_model().objects.create_user(username='staff', is_staff=True)

    def test_catalog_and_detail(self):
        self.assertContains(self.client.get(reverse('home')), self.perfume.name)
        self.assertContains(
            self.client.get(reverse('detail', args=[self.perfume.pk])),
            self.perfume.name,
        )

    def test_signup_logs_customer_in(self):
        response = self.client.post(reverse('signup'), {
            'username': 'new_customer',
            'password1': 'Fresh-Cedar-72-river',
            'password2': 'Fresh-Cedar-72-river',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_cart_requires_login(self):
        response = self.client.get(reverse('cart'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('cart')}")

    def test_cart_add_total_and_remove(self):
        self.client.force_login(self.customer)
        add = reverse('add_to_cart', args=[self.perfume.pk])
        detail = reverse('detail', args=[self.perfume.pk])
        self.assertEqual(self.client.get(add).status_code, 405)
        self.assertRedirects(self.client.post(add, HTTP_REFERER=detail), detail)
        self.client.post(add)
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.context['total'], 240)
        self.assertEqual(response.context['items'][0]['qty'], 2)
        self.client.post(reverse('remove_from_cart', args=[self.perfume.pk]))
        self.assertEqual(self.client.get(reverse('cart')).context['items'], [])

    def test_sold_out_item_cannot_be_added(self):
        self.perfume.in_stock = False
        self.perfume.save(update_fields=['in_stock'])
        self.client.post(reverse('add_to_cart', args=[self.perfume.pk]))
        self.assertEqual(self.client.session.get('cart', {}), {})

    def test_cart_post_requires_csrf_token(self):
        browser = Client(enforce_csrf_checks=True)
        detail = reverse('detail', args=[self.perfume.pk])
        add = reverse('add_to_cart', args=[self.perfume.pk])
        browser.get(detail)
        self.assertEqual(browser.post(add).status_code, 403)
        token = browser.cookies['csrftoken'].value
        self.assertRedirects(browser.post(add, {'csrfmiddlewaretoken': token}), reverse('home'))

    def test_api_reads_are_public_but_writes_require_staff(self):
        url = reverse('perfume-list')
        payload = {'name': 'Rose', 'brand': 'Ambre', 'price': '100.00', 'size_ml': 50}
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.customer)
        self.assertEqual(self.client.post(url, payload).status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(url, payload).status_code, 201)

    def test_private_cart_disables_browser_caching(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('cart'))
        self.assertIn('private', response.headers['Cache-Control'])
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_https_settings_redirect_and_protect_cookies(self):
        with self.settings(
            SECURE_SSL_REDIRECT=True, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True,
        ):
            home = reverse('home')
            response = self.client.get(home)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.url, 'https://testserver/')
            self.client.force_login(self.customer)
            response = self.client.get(
                reverse('detail', args=[self.perfume.pk]), secure=True,
            )
            self.assertTrue(response.cookies['csrftoken']['secure'])
