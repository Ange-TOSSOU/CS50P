#pip install requests
import requests


def get_artists(query, limit):
    try:
        response = requests.get(
            "https://api.artic.edu/api/v1/agents/search",
            {'q': query, "limit": limit}
        )
        response.raise_for_status()
    except requests.HTTPError:
        print("Couldn't complete request!")
        return
    
    content = response.json()
    return [artist["title"] for artist in content["data"]]
