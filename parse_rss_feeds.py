import requests
import feedparser
import pandas as pd
from datetime import datetime

def download_attachment(url, filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True,timeout=10, headers={"User-Agent":"Mozilla/5.0"})
    
    # Check if the request was successful
    if response.status_code == 200:
        # Open the local file in binary write mode
        with open("attachments/"+filename, 'wb') as file:
            # Write the content to the file in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File saved as {filename}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def download_rss_feeds():
    # URL of the NSE India Announcements RSS feed
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"

    # Fetch the data using requests with TLS 1.3 support
    try:

        response = requests.get(rss_url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        response.raise_for_status()  # Raise an error if the request was unsuccessful
        content = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the feed: {e}")

        # Parse the content with feedparser
    feed = feedparser.parse(content)

    announcement_data = []

    # Check if feed was parsed
    if not feed.entries:
        print("Feedparser did not parse any entries.")
    else:
        # Print the feed title
        print(f"Feed Title: {feed.feed.title}\n")

        # Loop through the entries (items) in the feed
        for entry in feed.entries:
            file_name = entry.link.split('/')[-1]

            if file_name and entry.link.startswith("https://"):
                try:
                    download_attachment(entry.link,file_name)
                except Exception as e:
                    print("Issue")

            announcement_data.append({
                "Title":entry.title,
                "Link":entry.link,
                "Published":entry.published,
                "Description":entry.description,
                "Filename":file_name
            })
            print(announcement_data[-1])

        df = pd.DataFrame(announcement_data)
        df = df.sort_values(by=['Published'])

        file_path = "daily_announcements/announcement_"+datetime.strftime(datetime.now(),"%Y%m%d")+".csv"
        df.to_csv(file_path,index=False)
        print("Activity Complete")

download_rss_feeds()
