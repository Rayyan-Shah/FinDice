# Financial Reports Django App

A simple Django application for tracking transactions, budgets, and financial goals, and viewing interactive reports. Supports charting with Google Charts.
## Dear Team
Please read through this to understand how the AI portion works (how to add your api). Don't just ChatGPT this and hope it figuers out how to update the code to work. If you're going to change anything involving AI or global changes please coordinate with the rest of the team so no errors occur. Only push to branches then PR.
 -Abdulaziz
  
## Current Bugs🪲

- Can’t change future or past month budgets
- Can’t choose income or cash in adding transactions, thus not being able to give a proper graph that shows changes in income.
- Generic dynamic summary text doesn't pull all the information properly. (budget.amount if budget else 'N/A' seems to always return 'N/A'. Also this looks awful it should be a completely different summary text if no budget is found or some other work around involving AI) [Removed component for now]
- "You have successfully registered!" message pops up incorrectly when opening add transaction (recreate: user creates account --> lands homepage --> click add transaction --> incorrect pop up here 
## Features
- User authentication (registration, login, logout)
- Record income, expenses, and cash transactions
- Set monthly budgets and financial goals
- View dynamic financial summary and interactive charts (pie & line)

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



---

*Happy tracking!*


