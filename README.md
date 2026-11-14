# Ambre Perfumes

A Django perfume shop with a catalog, session-based cart, accounts and a REST API.

## Run on Windows

Open PowerShell in this folder with a Python 3.14 virtual environment activated:

```powershell
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. To add perfumes, run `python manage.py createsuperuser` and use `/admin/`. To reuse your local catalog and accounts, copy a backup of your original `db.sqlite3` to this folder before migrating. Keep your local database and signing key out of GitHub.

## Run with Docker Compose

With Docker Desktop running in Linux container mode:

```powershell
$env:DJANGO_SECRET_KEY = Read-Host "Enter a strong local signing key"
$env:AMBRE_PORT = '8080'
docker compose up --build --wait
docker compose ps
docker compose exec web python manage.py createsuperuser
```

Open http://127.0.0.1:8080/. Compose runs migrations at startup and checks that the homepage responds. The named volume stores SQLite between restarts. Run `docker compose down` to stop the service.

## Tests and GitHub Actions

```powershell
python manage.py test
python -m pip install -r requirements-dev.txt
python manage.py test myapp.browser_checks
```

The browser test needs Chrome. Selenium Manager can resolve ChromeDriver, or you can set `CHROME_BINARY` and `CHROMEDRIVER` to installed executable paths. Django creates a separate database during tests.

The Actions workflow runs Django and Chrome tests on pushes and pull requests. A second job builds the Compose service, checks the homepage over HTTP and runs the Django tests in the container.

## Security and scalability

Production settings use a stable `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS` set to the site's domain. Configure TLS on the host and make sure Django detects secure requests. Django then redirects HTTP and uses Secure session and CSRF cookies. Enable HSTS with `DJANGO_HSTS_SECONDS` after verifying HTTPS on the deployment. Configure static file serving and SMTP on the host if needed.

The cart uses Django sessions and retrieves its products in a single bulk lookup. Cart responses instruct browsers and shared caches to avoid storing them. Django autoescapes template values and checks CSRF tokens on submitted forms. Only staff can write through the catalog API. Adding to the cart redirects within the site.

The local package uses one service and SQLite. For a multi-instance deployment, use a shared database for the catalog and sessions, configure a load balancer with health checks, then evaluate autoscaling and database replicas using measured traffic. Use a shared cache only for suitable public data.
