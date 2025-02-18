"""
Get the list of product and release from the Buildly Insights API
https://labs-api.buildly.io/docs/
"""

import requests
import json
import os
from .models import Punchlist, Product


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
    
def update_punchlist(product, labs_release_id=None):
    # create a new punchlist if it does not exist for each product
    get_punchlist = Punchlist.objects.filter(labs_product_id=product.product_uuid, labs_release_id=labs_release_id)
    if get_punchlist.exists():
        print('Punchlist already exists for product %s' % product['name'])
        punchlist = get_punchlist.first()
    else:
        punchlist = Punchlist.objects.create(
            title="Default punchlist",
            catagory="Punchlist",
            is_public=True,
            description="Default punclist created by the system.",
            labs_product_id=product['product_uuid'],
            labs_product_name=product['name'],
            labs_organization_uuid=product['organization_uuid'],
            labs_release_id=labs_release_id,
            product=product,
        )
        print('Punchlist created for product %s' % product['name'])

def get_labs_data():
    # update labs data with releases
    products = get_products()
    print('Products count: %s' % len(products))
    if products is None:
        return None 
    for product in products:
        get_product = Product.objects.filter(product_uuid=product['product_uuid'])
        if get_product.exists():
            print('Product %s already exists' % product['name'])
            collab_product = get_product.first()
        else:
            collab_product = Product.objects.create(
                name=product['name'],
                description=product['description'],
                product_info=product['product_info'] or '',
                product_uuid=product['product_uuid'],
                organization_uuid=product['organization_uuid'],
                product_team=product['product_team'],
                start_date=product['start_date'],
                end_date=product['end_date'],
            )
            print('Product %s created' % product['name'])

            releases = get_releases(product['product_uuid'])
            for release in releases:
                labs_release_id = release['release_uuid']

                # update punchlist with the labs data or create a new punchlist
                update_punchlist(collab_product, labs_release_id)
