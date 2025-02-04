"""
Get the list of product and release from the Buildly Insights API
https://labs-api.buildly.io/docs/
"""

import requests
import json
import os
from .models import Punchlist 


def get_products():
    url = "https://labs-api.buildly.io/product/product/"
    headers = { "Authorization": f"Bearer {str(os.getenv('INSIGHTS_API_KEY'))}" }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  
    else:
        return None 
    
def get_releases(product_id):
    url = f"https://labs-api.buildly.io/release/release/?product_uuid={product_id}"
    headers = { "Authorization": f"Bearer {str(os.getenv('INSIGHTS_API_KEY'))}" }
    response = requests.get(url, headers=headers)   
    
    if response.status_code == 200:
        return response.json()  
    else:
        return None
    
def update_punchlist(product_id=None, product_name=None, organization_uuid=None, release_id=None):
    # create a new punchlist if it does not exist for each product
    get_punchlist = Punchlist.objects.filter(labs_product_id=product_id)
    if get_punchlist.exists():
        punchlist = get_punchlist.first()
    else:
        punchlist = Punchlist(labs_product_id=product_id, labs_product_name=product_name, labs_organization_uuid=organization_uuid, labs_release_id=release_id)

def get_labs_data():
    # update labs data with releases
    products = get_products()
    if products is None:
        return None 
    for product in products:
        labs_product_id = product['product_uuid']
        labs_product_name = product['name']
        labs_organization_uuid = product['organization_uuid']
        print(labs_product_name)
        # update punchlist with the labs data or create a new punchlist
        update_punchlist(product_id=labs_product_id, product_name=labs_product_name, organization_uuid=labs_organization_uuid)
        releases = get_releases(labs_product_id)
        for release in releases:
            labs_release_id = json.dumps(releases) 
            release_name = release['name']
            update_punchlist(product_id=labs_product_id, product_name=labs_product_name, release_id=labs_release_id)
            print(labs_product_name, labs_release_id)        
    
        
        
    