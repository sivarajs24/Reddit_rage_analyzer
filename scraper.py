import os
import json
import requests
import time
import re
import xml.etree.ElementTree as ET


def scrape_reddit(product_name: str, limit_per_sub: int = 15, custom_subreddits: list = None):
    """
    Scrapes Reddit data by hitting the public RSS search feeds.
    Bypasses Reddit's 403 blocks on JSON endpoints.
    """
    collected_data = []
    
    # Custom subreddits fallback - remove tech-bias by default
    # "all" is a special keyword we'll use for global search
    target_subs = custom_subreddits if custom_subreddits else ["all"]
    
    # Heuristic: Add the product name itself as a guessed official subreddit
    guessed_sub = product_name.lower().replace(" ", "")
    if guessed_sub not in target_subs and not custom_subreddits:
        target_subs.insert(0, guessed_sub)
        
    print(f"Scraping Reddit RSS for '{product_name}' in subreddits: {', '.join(target_subs)}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    query = re.sub(r'[^a-zA-Z0-9 ]', '', product_name).replace(" ", "%20")
    
    for sub_name in target_subs:
        try:
            # If "all" is specified, do a global search across all of Reddit
            if sub_name == "all":
                url = f"https://www.reddit.com/search.rss?q={query}&sort=relevance"
            else:
                url = f"https://www.reddit.com/r/{sub_name}/search.rss?q={query}&restrict_sr=1"
            
            # Simple retry loop
            for attempt in range(2):
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    entries = root.findall('atom:entry', ns)
                    
                    for index, entry in enumerate(entries[:limit_per_sub]):
                        title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ""
                        content = entry.find('atom:content', ns).text if entry.find('atom:content', ns) is not None else ""
                        link = entry.find('atom:link', ns).attrib.get('href', '') if entry.find('atom:link', ns) is not None else ""
                        updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
                        
                        # Try to clean HTML from RSS content slightly
                        content = re.sub(r'<[^>]+>', ' ', content)
                        
                        item = {
                            "id": f"{sub_name}_{index}",
                            "type": "post",
                            "title": title,
                            "body": content,
                            "upvotes": 0, # RSS doesn't provide upvotes
                            "subreddit": sub_name,
                            "timestamp": 0,
                            "datetime": updated,
                            "url": link
                        }
                        collected_data.append(item)
                    break # Success, exit retry loop
                elif response.status_code == 429:
                    print(f"Rate limited (429) on r/{sub_name}. Waiting 5 seconds...")
                    time.sleep(5.0)
                elif response.status_code == 404:
                    print(f"Subreddit r/{sub_name} not found. Skipping.")
                    break
                else:
                    print(f"Error fetching from {url}: Status Code {response.status_code}")
                    break
                    
            time.sleep(3.0) # Avoid rate limiting for the next subreddit
                
        except Exception as e:
            print(f"Error scraping {sub_name}: {e}")

    # Deduplicate by URL
    unique_data = {item['url']: item for item in collected_data if item['url']}.values()
    final_data = list(unique_data)

    os.makedirs("data", exist_ok=True)
    output_path = f"data/raw_{product_name.replace(' ', '_').lower()}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4)
        
    print(f"Scraped {len(final_data)} items. Saved to {output_path}")
    return final_data

if __name__ == "__main__":
    sample_data = scrape_reddit("Instagram", limit_per_sub=5)
    print(f"Sample data gathered: {len(sample_data)} records.")
