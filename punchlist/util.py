import openai
from django.http import JsonResponse
# Removed unused import
from django.conf import settings
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Removed unused import

openai.api_key = settings.OPENAI_API_KEY

class RateLimitError(Exception):
    pass

def preprocess_application_data(application):
    """
    Preprocess the application data to create a comprehensive summary text.
    Adjust the details as per your model's requirements.
    
    'name': self.name,
    'description': self.description,
    'product_info': self.product_info,
    """
    details = [
        f"Product Description: {application['description']}",
        f"Name: {application['name']}",
        f"Product Information: {application['product_info']}",
        # Add more fields as necessary
    ]
    return " ".join(details)

def evaluate_product_idea(application):
    """
    Evaluate the detailed startup application using ChatGPT for scoring based on specific criteria.
    """
    
    # Define the application summary from preprocess_application_data
    application_summary = preprocess_application_data(application)
    
    try:
        # Generate the review using ChatGPT
        completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Please review and evaluate the software product idea: Evaluation Criteria:\n1. Originality\n2. Marketability\n3. Feasibility\n4. Completeness\n\nPlease provide your summary text of how good or bad the idea is and individual numeric scores for each criterion out of 100 each:\n\nOriginality Score:\nMarketability Score:\nFeasibility Score:\nCompleteness Score:"},
            {"role": "user", "content": application_summary}
        ]
        )
        print(completion.choices[0].message.content)
        score_text = completion.choices[0].message.content
        
        # Generate Review using Gemini
        import google.generativeai as genai
        import os

        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        response = genai.generate_text(
            model="gemini-1.0-pro-latest",
            prompt=f"Please review and evaluate the software product idea: Evaluation Criteria:\n1. Originality\n2. Marketability\n3. Feasibility\n4. Completeness\n\nPlease provide your summary text of how good or bad the idea is and individual numeric scores for each criterion out of 100 each:\n\nOriginality Score:\nMarketability Score:\nFeasibility Score:\nCompleteness Score: {application_summary}"
        )
        
        gemini_score_text = response
                
        if completion.choices and completion.choices[0].message:
            
            # Extract individual scores from the score text
            score_lines = score_text.split('\n')

            # Find and extract the scores
            scores = {}
            for line in score_lines:
                if "Score" in line:
                    criterion, score = line.split(":")
                    scores[criterion.strip()] = int(score.split("/")[0])
            score_text = score_text.split('\n')
            originality_score = scores.get('Originality Score', 0)
            marketability_score = scores.get('Marketability Score', 0)
            feasibility_score = scores.get('Feasibility Score', 0)
            completeness_score = scores.get('Completeness Score', 0)
        else:
            score_text = "AI Failed to Summarize the Application. Please review manually."
            originality_score = 0
            marketability_score = 0
            feasibility_score = 0
            completeness_score = 0

        logging.info(f"openAI response: {score_text}")
        if gemini_score_text and isinstance(gemini_score_text, str):
            
            # Extract individual scores from the score text
            score_lines = gemini_score_text.split('\n')

            # Find and extract the scores
            scores = {}
            for line in score_lines:
                if "Score" in line:
                    criterion, score = line.split(":")
                    scores[criterion.strip()] = int(score.split("/")[0])

            gemini_originality_score = scores.get('Originality Score', 0)
            gemini_marketability_score = scores.get('Marketability Score', 0)
            gemini_feasibility_score = scores.get('Feasibility Score', 0)
            gemini_completeness_score = scores.get('Completeness Score', 0)
        else:
            gemini_score_text = "Gemini AI Failed to Summarize the Application. Please review manually."
            gemini_originality_score = 0
            gemini_marketability_score = 0
            gemini_feasibility_score = 0
            gemini_completeness_score = 0

        logging.info(f"openAI response: {score_text}")

    except Exception as e: 
        logging.error(f"Rate Limit Error: {str(e)}")
        scores = "0"
        score_text = "0"
        originality_score = "0"
        marketability_score = "0"
        feasibility_score = "0"
        completeness_score = "0"
        gemini_score_text = "0"
        gemini_originality_score = "0"
        gemini_marketability_score = "0"
        gemini_feasibility_score = "0"
        gemini_completeness_score = "0"
        
        # Send an email using SendGrid API
        message = Mail(
            from_email='foundry@buildly.io',
            to_emails='greg@buildly.io',
            subject='Open AI Rate Limit Exceeded',
            html_content='<strong>Check the Foundry</strong>')
        
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))
            
    return score_text, originality_score, marketability_score, feasibility_score, completeness_score, gemini_score_text, gemini_originality_score, gemini_marketability_score, gemini_feasibility_score, gemini_completeness_score

def analyze_ai_response(response):
    """
    Parses the structured response from the OpenAI API based on the given prompt.
    The function extracts scores for originality, marketability, feasibility,
    and completeness, as well as a summary from the text.
    """
    text = response.choices[0].text.strip()

    # Initialize a dictionary to hold the scores and summary
    analysis = {
        'originality_score': 0.0,
        'marketability_score': 0.0,
        'feasibility_score': 0.0,
        'completeness_score': 0.0,
        'summary': "",
    }

    # Regex patterns to find scores and summary in the response
    score_pattern = r"originality: (\d\.\d+)|marketability: (\d\.\d+)|feasibility: (\d\.\d+)|completeness: (\d\.\d+)"
    summary_pattern = r"summary: (.+)"

    # Extract scores using regex
    matches = re.finditer(score_pattern, text, re.IGNORECASE)
    for match in matches:
        if match.group(1):
            analysis['originality_score'] = float(match.group(1))
        elif match.group(2):
            analysis['marketability_score'] = float(match.group(2))
        elif match.group(3):
            analysis['feasibility_score'] = float(match.group(3))
        elif match.group(4):
            analysis['completeness_score'] = float(match.group(4))

    # Extract summary using regex
    summary_match = re.search(summary_pattern, text, re.IGNORECASE)
    if summary_match:
        analysis['summary'] = summary_match.group(1).strip()  # Ensure whitespace is removed

    return analysis
