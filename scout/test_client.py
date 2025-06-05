import requests
import json

def test_request():
    # Replace with your actual message
    message = "Find papers about large language models"
    n = 3  # Number of papers to fetch
    
    # Make the request
    response = requests.post(
        "http://localhost:8000/stream",
        params={"message": message, "n": n}
    )
    
    print(f"Status: {response.status_code}")
    
    # Parse and print the JSON response
    try:
        json_response = response.json()
        print("\nReceived JSON:")
        print(json.dumps(json_response, indent=2))
    except json.JSONDecodeError:
        print(f"Failed to parse JSON: {response.text}")

if __name__ == "__main__":
    test_request() 