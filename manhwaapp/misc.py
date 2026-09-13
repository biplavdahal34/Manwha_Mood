import requests


def latest_list(limit=8):
    url = "https://api.mangadex.org"
    
    r = requests.get(
    f"{url}/manga",
    params={"order[createdAt]": "desc",
        "limit": limit,
        "includes[]": ["cover_art"],
        "contentRating[]": ["safe", "suggestive", "erotica"],
        "order[relevance]": "desc",}
    )

    if r.status_code == 200:
        response = r.json()['data']
        return {"api_ok" :True, "response": response}
    return {"api_ok":False, "response_json": None}

def popular_list(limit=8):
    url = "https://api.mangadex.org"
    
    r = requests.get(
    f"{url}/manga",
    params={"order[followedCount]": "desc",
        "limit": limit,
        "includes[]": ["cover_art"],
        "contentRating[]": ["safe", "suggestive", "erotica"],
        "order[relevance]": "desc",
        }
    )

    if r.status_code == 200:
        response = r.json()['data']
        return {"api_ok" :True, "response": response}
    return {"api_ok":False, "response_json": None}


def get_manhwa_byname(manhwa_name):
    url = "https://api.mangadex.org"
    
    r = requests.get(
    f"{url}/manga",
    params={
    "title": manhwa_name,
    "includes[]" : ["cover_art"],
    "order[relevance]": "desc",
    }
    )

    if r.status_code == 200:
        response = r.json()['data']
        return {"api_ok" :True, "response": response}
    return {"api_ok":False, "response_json": None}

def get_manhwa_byid(manhwa_id):
    url = f"https://api.mangadex.org/manga/{manhwa_id}"
    
    r = requests.get(
    f"{url}",
    params={
    "includes[]" : ["cover_art",'artist','author']
     }
    )

    if r.status_code == 200:
        response = r.json()['data']
        return {"api_ok" :True, "response": response}
    return {"api_ok":False, "response_json": None}
