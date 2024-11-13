from openai import OpenAI
from django.http import JsonResponse, HttpRequest
from django.conf import settings
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# aggregate_reviews.py
from bs4 import BeautifulSoup
import requests
from django.utils import timezone
from .models import DevelopmentAgency, AgencyReview, AgencyAggregate

API_KEYS = {
    "google": settings.GOOGLE_PLACES_API_KEY,
    "yelp": settings.YELP_API_KEY,
    # Add any other API keys needed
}

def get_google_reviews(agency):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": agency.name,
        "inputtype": "textquery",
        "fields": "place_id,rating,user_ratings_total",
        "key": API_KEYS["google"]
    }
    response = requests.get(url, params=params)
    reviews = []
    if response.status_code == 200:
        data = response.json()
        place_id = data.get("candidates", [{}])[0].get("place_id")
        if place_id:
            detail_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEYS['google']}&fields=reviews,url"
            detail_response = requests.get(detail_url)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                url = detail_data.get("result", {}).get("url", "")
                for review in detail_data.get("result", {}).get("reviews", []):
                    reviews.append({
                        "rating": review.get("rating"),
                        "text": review.get("text"),
                        "platform": "Google",
                        "review_link": url
                    })
    return reviews

def get_yelp_reviews(agency):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {API_KEYS['yelp']}"}
    params = {"term": agency.name, "location": "US", "limit": 5}
    response = requests.get(url, headers=headers, params=params)
    reviews = []
    if response.status_code == 200:
        businesses = response.json().get("businesses", [])
        for business in businesses:
            if "rating" in business:
                reviews.append({
                    "rating": business["rating"],
                    "text": business.get("snippet_text", ""),
                    "platform": "Yelp",
                    "review_link": business.get("url")
                })
    return reviews

def scrape_clutch_reviews(agency):
    reviews = []
    if agency.clutch_url:
        response = requests.get(agency.clutch_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for review_block in soup.find_all("div", class_="review"):
                rating = float(review_block.find("span", class_="rating").text.strip())
                text = review_block.find("p", class_="review-text").text.strip()
                reviews.append({
                    "rating": rating,
                    "text": text,
                    "platform": "Clutch",
                    "review_link": agency.clutch_url
                })
    return reviews

def aggregate_reviews(agency):
    # Gather reviews from each API and Clutch scraping
    reviews = (
        get_google_reviews(agency) +
        get_yelp_reviews(agency) +
        scrape_clutch_reviews(agency)
    )

    # Save each review to the database and calculate aggregate rating
    total_rating = 0
    for review in reviews:
        total_rating += review["rating"]
        AgencyReview.objects.create(
            agency=agency,
            platform=review["platform"],
            rating=review["rating"],
            review_text=review["text"],
            review_link=review["review_link"]
        )

    # Aggregate average score and save
    review_count = len(reviews)
    if review_count > 0:
        average_rating = total_rating / review_count
        aggregate, created = AgencyAggregate.objects.update_or_create(
            agency=agency,
            defaults={
                "average_rating": average_rating,
                "review_count": review_count,
                "last_checked": timezone.now()
            }
        )
        return aggregate
    return None

# Main function to run the aggregation
def run_aggregation(agency_name):
    try:
        agency = DevelopmentAgency.objects.get(name=agency_name)
    except DevelopmentAgency.DoesNotExist:
        print(f"Agency {agency_name} not found.")
        return

    result = aggregate_reviews(agency)
    if result:
        print(f"Aggregated Score for {agency.name}: {result.average_rating} ({result.review_count} reviews)")
    else:
        print(f"No reviews found for {agency.name}")

# Example usage
def check_all_agencies():
    DevelopmentAgency.objects.all()
    for agency in DevelopmentAgency.objects.all():
        run_aggregation(agency.name)
