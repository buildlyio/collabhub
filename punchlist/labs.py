"""
Get the list of product and release from the Buildly Insights API
https://insights-api.buildly.io/docs/
"""

import requests
import json
import os
from .models import Punchlist 


def get_products():
    url = "https://insights-api.buildly.io/product/product/"
    headers = { "Authorization  ": f"Token {os.environ.get('INSIGHTS_API_KEY')}" } 
    print(url)
    print(headers)
    response = requests.get(url, headers=headers)   
    
    print(response)
    print(response.json())
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        return response.json()  
    else:
        return None 
    
def get_releases(product_id):
    url = f"https://insights-api.buildly.io/release/release/?product_uuid={product_id}"
    headers = { "Authorization  ": f"Token {os.environ.get('INSIGHTS_API_KEY')}" }     
    response = requests.get(url, headers=headers)   
    
    if response.status_code == 200:
        return response.json()  
    else:
        return None
    
def update_punchlist(product_id, release_id):
    # create a new punchlist if it does not exist for each product
    get_punchlist = Punchlist.objects.filter(product_id=product_id)
    if get_punchlist.exists():
        punchlist = get_punchlist.first()
    else:
        punchlist = Punchlist(product_id=product_id)

def get_labs_data():
    # update labs data with releases
    products = get_products()
    if products is None:
        return None 
    for product in products:
        labs_product_id = product['id']
        labs_product_name = product['name']
        labs_organization_uuid = product['organization_uuid']
        print(labs_product_name)
        # update punchlist with the labs data or create a new punchlist
        update_punchlist(labs_product_id, labs_product_name, labs_organization_uuid)
        releases = get_releases(labs_product_id)
        for release in releases:
            labs_release_id = json.dumps(releases) 
            release_name = release['name']
            update_punchlist(labs_product_id,labs_product_name,labs_release_id)
            print(labs_product_name, labs_release_id)        
    
        
        
    