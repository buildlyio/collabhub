import requests
import json
import os
from django.conf import settings
from .models import Punchlist

# Function to get an OAuth token
def get_oauth_token():
    """
    Fetch an OAuth token from the /oauth/login/ endpoint using username, password, and client_id.
    """
    token_url = settings.LABS_TOKEN_URL + "/oauth/login/"
    username = getattr(settings, 'LABS_USERNAME', os.getenv('LABS_USERNAME'))
    password = getattr(settings, 'LABS_PASSWORD', os.getenv('LABS_PASSWORD'))
    client_id = getattr(settings, 'LABS_CLIENT_ID', os.getenv('LABS_CLIENT_ID'))
    client_secret = getattr(settings, 'LABS_CLIENT_SECRET', os.getenv('LABS_CLIENT_SECRET'))

    if not username or not password or not client_id:
        raise Exception("LABS_USERNAME, LABS_PASSWORD, and LABS_CLIENT_ID must be set in Django settings or environment variables.")

    payload = {
        "username": username,
        "password": password,
        "client_id": client_id,
    }

    print("Payload JSON for the request:", json.dumps(payload, indent=4))  # Output the JSON payload for debugging

    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")  # Log the raw response content
        raise Exception(f"Error connecting to {token_url}: {response.status_code} {response.text}")

    if response.status_code == 200:  # Assuming 200 is the success status code
        try:
            token_data = response.json()
            return token_data.get('access_token')  # Return only the access token
        except json.JSONDecodeError:
            print(f"Response Text (not JSON): {response.text}")
            raise Exception("Failed to decode JSON response from the server.")
    else:
        raise Exception(f"Failed to retrieve OAuth token: {response.status_code} {response.text}")

# Function to get products
def get_products():
    token = get_oauth_token()
    url = settings.LABS_TOKEN_URL + "product/product/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get releases
def get_releases(product_id):
    token = get_oauth_token()
    url = settings.LABS_TOKEN_URL + f"release/release/?product_uuid={product_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to update punchlist
def update_punchlist(product_id=None, product_name=None, organization_uuid=None, release_id=None):
    get_punchlist = Punchlist.objects.filter(labs_product_id=product_id)
    if get_punchlist.exists():
        punchlist = get_punchlist.first()
    else:
        punchlist = Punchlist(
            labs_product_id=product_id,
            labs_product_name=product_name,
            labs_organization_uuid=organization_uuid,
            labs_release_id=release_id
        )

# Function to get labs data
def get_labs_data():
    products = get_products()
    if products is None:
        return None
    for product in products:
        labs_product_id = product['product_uuid']
        labs_product_name = product['name']
        labs_organization_uuid = product['organization_uuid']
        print(labs_product_name)
        update_punchlist(product_id=labs_product_id, product_name=labs_product_name, organization_uuid=labs_organization_uuid)
        releases = get_releases(labs_product_id)
        for release in releases:
            labs_release_id = release['release_uuid']
            release_name = release['name']
            update_punchlist(product_id=labs_product_id, product_name=labs_product_name, release_id=labs_release_id)
            print(labs_product_name, labs_release_id)