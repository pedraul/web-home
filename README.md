# Services portal

A Django site for a single company: visitors find a service and open its external website; staff manage the list from a dashboard.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| URL | What it is |
| --- | --- |
| `/` | Image slideshow, scrolling text bands, and the service tiles |
| `/about/`, `/contact/`, `/support/` | About (live stats), contact form, service status + FAQs |
| `/dashboard/` | Staff dashboard: add, edit, publish/draft, delete (with undo), reset sample data |
| `/admin/` | Django admin: logo, moving text, home page slides, contact details, FAQs, contact messages |

Uploaded images are stored in `media/`. Slides without a photo use the built-in illustrations in `static/img/`.

On PythonAnywhere, add a static-files mapping in the Web tab with URL `/media/` and the full filesystem path to this project's `media/` directory. Keep that directory on persistent storage; uploaded files are not included in Git.

Sign in to the dashboard with a staff account's email (or username) and password.

## Notes

- Services, company details and FAQs are sample content: replace them from the dashboard and `/admin/`.
- Contact form messages are saved (see **Contact messages** in the admin) and emailed to the contact address. In development the email is printed to the terminal; set an SMTP backend in `portal/settings.py` before going live.
- Before deployment: set a private `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, and serve static files.

Run the tests with `python manage.py test services`.
