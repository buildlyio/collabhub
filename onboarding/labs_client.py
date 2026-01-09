"""
Labs API Client for CollabHub

This client handles all API calls from CollabHub to Labs.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class LabsClient:
    """Client for making API calls to Buildly Labs"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'LABS_API_URL', 'https://labs.buildly.io/api')
        self.api_key = getattr(settings, 'LABS_API_KEY', None)
        self.timeout = 30
    
    def _get_headers(self):
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make an HTTP request to Labs API"""
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Labs API timeout: {endpoint}")
            raise LabsAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            logger.error(f"Labs API connection error: {endpoint}")
            raise LabsAPIError("Could not connect to Labs API")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Labs API HTTP error: {e}")
            raise LabsAPIError(f"HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Labs API error: {e}")
            raise LabsAPIError(str(e))
    
    # ==================== Referral API ====================
    
    def register_referral(self, referral_code, referrer_email, referred_email, referred_user_id=None):
        """
        Register a new referral with Labs.
        
        Called when a user signs up via a CollabHub referral link.
        """
        data = {
            'referral_code': referral_code,
            'referrer_email': referrer_email,
            'referred_email': referred_email,
            'referred_user_id': referred_user_id,
            'source': 'collabhub',
        }
        return self._make_request('POST', '/referrals/register/', data=data)
    
    def get_referral_stats(self, referrer_email):
        """
        Get referral statistics for a user.
        
        Returns total referrals, points earned, redemption options, etc.
        """
        return self._make_request('GET', '/referrals/stats/', params={'referrer_email': referrer_email})
    
    def redeem_referral_points(self, referrer_email, redemption_option_id):
        """
        Redeem referral points for a reward.
        """
        data = {
            'referrer_email': referrer_email,
            'redemption_option_id': redemption_option_id,
        }
        return self._make_request('POST', '/referrals/redeem/', data=data)
    
    def get_redemption_options(self):
        """
        Get available redemption options.
        """
        return self._make_request('GET', '/referrals/redemption-options/')
    
    # ==================== User Sync API ====================
    
    def sync_user(self, user_data):
        """
        Sync user data to Labs.
        
        user_data should include:
        - email
        - name
        - collabhub_user_id
        - skills (optional)
        - certifications (optional)
        """
        return self._make_request('POST', '/users/sync/', data=user_data)
    
    def get_user_labs_profile(self, email):
        """
        Get a user's Labs profile and activity.
        """
        return self._make_request('GET', '/users/profile/', params={'email': email})
    
    # ==================== Health Check ====================
    
    def health_check(self):
        """Check if Labs API is available"""
        try:
            response = self._make_request('GET', '/health/')
            return True, response
        except LabsAPIError as e:
            return False, str(e)


class LabsAPIError(Exception):
    """Exception for Labs API errors"""
    pass


# Singleton instance
_labs_client = None

def get_labs_client():
    """Get or create Labs client instance"""
    global _labs_client
    if _labs_client is None:
        _labs_client = LabsClient()
    return _labs_client
