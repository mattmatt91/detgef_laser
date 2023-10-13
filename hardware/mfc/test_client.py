import requests

url = "http://localhost:8000/set_points"  # Replace with your FastAPI app's URL
data = {"dry": 50, "wet": 500}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print("Response:", result)
