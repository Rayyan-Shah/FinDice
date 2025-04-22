# Financial Reports Django App

A simple Django application for tracking transactions, budgets, and financial goals, and viewing interactive reports. Supports charting with Google Charts.

## Features
- User authentication (registration, login, logout)
- Record income, expenses, and cash transactions
- Set monthly budgets and financial goals
- View dynamic financial summary and interactive charts (pie & line)

## Configuration
Create a `config.json` file at the project root (next to `manage.py`) with the following structure:

```json
{
  "SECRET_KEY": "your-django-secret-key-here",
  "DEBUG": true,
  "ALLOWED_HOSTS": ["localhost", "127.0.0.1"],
  "DATABASE": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "db.sqlite3"
  },
  "SAMBANOVA_API_KEY": "your-sambanova-api-key-here"
}
```

- **SECRET_KEY**: Django secret key for cryptographic signing
- **DEBUG**: `true` for development, `false` in production
- **ALLOWED_HOSTS**: list of host/domain names your site will serve
- **DATABASE**: Django database settings (defaults to SQLite)
- **SAMBANOVA_API_KEY**: Your API key from SambaNova Systems for AI chat integration

### Loading `config.json` in `settings.py`
In your `settings.py`, load the config:

```python
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / 'config.json') as cfg_file:
    cfg = json.load(cfg_file)

SECRET_KEY = cfg['SECRET_KEY']
DEBUG = cfg['DEBUG']
ALLOWED_HOSTS = cfg['ALLOWED_HOSTS']

# Database config
DATABASES = {
    'default': cfg['DATABASE']
}

# SambaNova API key for AI (if using AI chat)
SAMBANOVA_API_KEY = cfg.get('SAMBANOVA_API_KEY')
```

## Database Migrations
Run migrations to create the database schema:

```bash
python manage.py migrate
```

## Create Superuser (optional)
To access Django admin:

```bash
python manage.py createsuperuser
```

## Running the Server
Start the development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and register a new user to get started.

## AI Chat Integration (Optional)
If you enable the AI chat on the `view_reports` page, the view will read `SAMBANOVA_API_KEY` from settings and call SambaNova's API. Ensure:

1. `SAMBANOVA_API_KEY` is set in `config.json`.
2. The `ai_chat` view uses:
   ```python
   import samba_api  # hypothetical SDK
   from django.conf import settings

   client = samba_api.Client(api_key=settings.SAMBANOVA_API_KEY)
   ```
3. The JavaScript in `view_reports.html` posts to `/ai-chat/` and expects JSON `{ reply: string }`.

To disable AI integration, remove or comment out the chat container and related scripts in `view_reports.html`, and delete the `ai_chat` view and URL.

## License
MIT

## Contributing
Feel free to open issues or submit pull requests. Please adhere to the existing code style and add tests for new features.

---

*Happy tracking!*

## Current Bugs🪲

- Can’t change future or past month budgets
- Can’t choose income or cash in adding transactions, thus not being able to give a proper graph that shows changes in income.