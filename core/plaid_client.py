# core/plaid_client.py
from plaid import Configuration, ApiClient
from plaid.api.plaid_api import PlaidApi
from django.conf import settings

# Create a Configuration object
configuration = Configuration(
    host=settings.PLAID_ENV,
    api_key={
        'clientId': settings.PLAID_CLIENT_ID,
        'secret': settings.PLAID_SECRET,
    }
)

# Create an ApiClient
api_client = ApiClient(configuration)

# Create PlaidApi object
client = PlaidApi(api_client)

