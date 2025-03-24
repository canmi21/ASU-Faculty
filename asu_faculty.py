import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import sys
import threading
from multiprocessing import Pool, Manager
from itertools import cycle

BASE_URL = "https://search.asu.edu/view/directory-profiles?page={}"  
PROFILE_URL = "https://search.asu.edu/profile/{}"  
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0"
]

spinner = cycle("|/-\\")
stop_spinner = False

def animate():
    while not stop_spinner:
        sys.stdout.write(f"\r {next(spinner)} ")
        sys.stdout.flush()
        time.sleep(0.1)

def get_email(profile_id, headers):
    response = requests.get(PROFILE_URL.format(profile_id), headers=headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    email_tag = soup.find("a", href=lambda x: x and x.startswith("mailto:"))
    return email_tag.text.strip() if email_tag else None

def scrape_page(page, queue):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    response = requests.get(BASE_URL.format(page), headers=headers)
    if response.status_code != 200:
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("tbody")
    if not table:
        return
    
    for row in table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) < 3:
            continue
        
        name_tag = columns[0].find("a")
        if not name_tag:
            continue

        name = name_tag.text.strip()
        profile_id = name_tag["href"].split("/")[-1]
        expertise = columns[1].text.strip()
        short_bio = columns[2].text.strip()
        email = get_email(profile_id, headers) or "N/A"
        
        if expertise and short_bio and email != "N/A":
            queue.put({"id": profile_id, "name": name, "email": email, "expertise": expertise, "short_bio": short_bio})
            sys.stdout.write(f"\r+ Found {name} ({email})\n")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\r- Dropped {name}             ")
            sys.stdout.flush()

def save_profiles_periodically(queue, stop_event):
    profiles_file = "asu_profiles.json"
    data = []
    
    if os.path.exists(profiles_file):
        with open(profiles_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    
    while not stop_event.is_set() or not queue.empty():
        try:
            profile = queue.get(timeout=1)
            data.append(profile)
            if len(data) % 10 == 0:
                with open(profiles_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                sys.stdout.write("- Data saved.\n")
                sys.stdout.flush()
        except Exception:
            continue
    
    with open(profiles_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        sys.stdout.write("\n - Data saved.\n")
        sys.stdout.flush()

def main():
    global stop_spinner
    start_page = int(input("? Enter start page: "))
    total_pages = int(input("? Enter number of pages to scrape: "))
    num_workers = int(input("? Enter number of threads: "))
    
    manager = Manager()
    queue = manager.Queue()
    stop_event = manager.Event()
    
    saver_thread = threading.Thread(target=save_profiles_periodically, args=(queue, stop_event))
    saver_thread.start()
    
    pages = list(range(start_page, start_page + total_pages))
    
    spinner_thread = threading.Thread(target=animate)
    spinner_thread.start()
    
    try:
        with Pool(num_workers) as pool:
            pool.starmap(scrape_page, [(page, queue) for page in pages])
    except KeyboardInterrupt:
        print("\nInterrupted, saving collected data...")
        pool.terminate()
        stop_event.set()
        saver_thread.join()
        stop_spinner = True
        spinner_thread.join()
        print(" - Data saved.")
        sys.exit(1)
    
    stop_event.set()
    saver_thread.join()
    stop_spinner = True
    spinner_thread.join()
    print("\n# Scraping completed.")

if __name__ == "__main__":
    main()