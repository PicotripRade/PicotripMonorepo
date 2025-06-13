from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class ApiKeys:
    aviation_edge_key = os.getenv('AVIATION_EDGE_KEY')
    groq_key = os.getenv('GROQ_KEY')
    openai_key = os.getenv('OPENAI_KEY')
    amadeus_api_key = os.getenv('AMADEUS_API_KEY')
    amadeus_api_secret = os.getenv('AMADEUS_API_SECRET')
    rh_key = os.getenv('RH_KEY')
    RateHawk_api_key = os.getenv('RATE_HAWK_API_KEY')
    RateHawk_api_secret = os.getenv('RATE_HAWK_API_SECRET')
