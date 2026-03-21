import requests
import json

# API endpoint'ini test et
url = "http://localhost:5000/subeler/1/makineler"

try:
    response = requests.get(url, allow_redirects=False)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Response text: {response.text[:1000]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
