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

def stats(manga_id):
    base_url = "https://api.mangadex.org"

    r = requests.get(f"{base_url}/statistics/manga/{manga_id}",
     params={'translatedLanguage[]': 'en'}
     )
     

    
    if r.status_code == 200:
       return r.json()["statistics"][manga_id]

def chapter_all(manga_id):
    base_url = "https://api.mangadex.org"

    r = requests.get(f"{base_url}/manga/{manga_id}/feed",
    params={"order[chapter]" : "desc",
    "translatedLanguage[]" : 'en'})
    chap_num = []
    for chapter in r.json()["data"]:
        chap_num.append(chapter['attributes']['chapter'])

    return {"response" : r.json(),"chap_num": chap_num} 

def get_page_id(chapter_id):
    base_url = "https://api.mangadex.org"

    r = requests.get(f"{base_url}/at-home/server/{chapter_id}"
    )
    if r.status_code != 200:
        print("at-home error:", r.status_code, r.text)
    r_json = r.json()
    print(r_json)
    host = r_json["baseUrl"]
    chapter_hash = r_json["chapter"]["hash"]
    data = r_json["chapter"]["data"]
    return {'data':data,'host': host,"chap_hash": chapter_hash}