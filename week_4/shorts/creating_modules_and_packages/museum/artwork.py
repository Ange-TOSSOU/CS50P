# pip install requests
import requests


def get_artworks(query, limit):
    try:
        response = requests.get(
            "https://api.artic.edu/api/v1/artworks/search", {"q": query, "limit": limit}
        )
        response.raise_for_status()
    except requests.HTTPError:
        print("Couldn't complete request!")
        return

    content = response.json()
    return [artwork["title"] for artwork in content["data"]]
