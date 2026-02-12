"""
Peloton Bearer Token Authentication
Based on Peloton-to-Garmin PR #806
Peloton now uses OAuth Bearer Tokens instead of session cookies
"""

import requests


class PelotonBearerAuth:
    def __init__(self):
        self.bearer_token = None
        self.user_id = None
        self.session = requests.Session()
    
    def set_bearer_token(self, token):
        """
        Set the bearer token for API authentication
        
        Args:
            token: OAuth bearer token from browser
        """
        self.bearer_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'peloton-platform': 'web',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Get user ID
        self.user_id = self._get_user_id()
        
        return bool(self.user_id)
    
    def _get_user_id(self):
        """Get user ID using bearer token"""
        try:
            response = self.session.get('https://api.onepeloton.com/api/me')
            
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            else:
                print(f"Failed to get user ID: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    def get_workouts(self, limit=5):
        """
        Fetch recent workouts
        
        Args:
            limit: Number of workouts to fetch
            
        Returns:
            list: Workout data
        """
        if not self.bearer_token or not self.user_id:
            raise Exception("Not authenticated. Please set bearer token first.")
        
        try:
            url = f"https://api.onepeloton.com/api/user/{self.user_id}/workouts"
            params = {
                'joins': 'ride,ride.instructor',
                'limit': limit,
                'page': 0
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"Error fetching workouts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching workouts: {e}")
            return []
    
    def get_workout_details(self, workout_id):
        """
        Fetch detailed workout performance data
        
        Args:
            workout_id: Peloton workout ID
            
        Returns:
            dict: Detailed workout data
        """
        if not self.bearer_token:
            raise Exception("Not authenticated. Please set bearer token first.")
        
        try:
            url = f"https://api.onepeloton.com/api/workout/{workout_id}/performance_graph"
            params = {'every_n': 5}
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching workout details: {e}")
            return None


def get_bearer_token_from_user():
    """
    Interactive function to get bearer token from user
    """
    print("=" * 70)
    print("PELOTON BEARER TOKEN AUTHENTICATION")
    print("=" * 70)
    print("\nHow to get your bearer token:")
    print("1. Open https://members.onepeloton.com in your browser")
    print("2. Log in to your account")
    print("3. Press F12 to open DevTools")
    print("4. Go to the Network tab")
    print("5. Refresh the page or click around")
    print("6. Find any request to 'api.onepeloton.com'")
    print("7. Look for 'Authorization: Bearer <token>' in the request headers")
    print("8. Copy the token (everything after 'Bearer ')")
    print("\n" + "=" * 70)
    
    token = input("\nPaste your bearer token here: ").strip()
    
    # Clean up the token if user included "Bearer " prefix
    if token.startswith("Bearer "):
        token = token[7:].strip()
    
    return token
