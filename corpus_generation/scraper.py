from bs4 import BeautifulSoup
from random import random
import os.path
import time
import requests
import cfscrape

BASE_URL = "https://www.betootaadvocate.com/category/"
START_TOKEN = "<|startoftext|>"
END_TOKEN = "<|endoftext|>"

scraper = cfscrape.create_scraper()


def get_url_from_category(category):
    return BASE_URL + category + "/"


def get_num_pages(base_url):
    page = requests.get(base_url)
    soup = BeautifulSoup(page.text, "html.parser")
    return int(soup.find("div", class_="page-nav").find("a", class_="last").string)


def get_article_urls_from_website(base_url, limit=None):
    urls = []
    num_pages = limit if limit != None else get_num_pages(base_url)
    for num in range(1, num_pages + 1):
        while True:
            try:
                print(f"Requesting page {num}\n")
                page = scraper.get(base_url + f"page/{num}/")
                soup = BeautifulSoup(page.content, "html.parser")
                articles = soup.find_all("div", class_="td_module_12")
                for article in articles:
                    url = article.find("h3").find("a").get("href")
                    urls.append(url)
                # Wait some time
                time.sleep(2 + 3 * random())
            except ConnectionError:
                print(
                    "Connecting error when requesting page, waiting 30 seconds before trying again..."
                )
                time.sleep(30)
                continue
            break
    return urls


def get_article_urls(category, limit=None):
    base_url = get_url_from_category(category)
    # if we already have the urls txt file, we just get the article urls from that
    # otherwise we need to scrape the urls themselves
    filename = f"url_{category}.txt"
    if os.path.exists(filename):
        # read the urls from the file
        with open(filename, "r") as f:
            return f.readlines()
    else:
        urls = get_article_urls_from_website(base_url, limit)
        with open(filename, "w") as f:
            # now have all the urls, write them to a file
            f.writelines(f"{url}\n" for url in urls)
        print("Please review the urls...\n")
        exit()


# Gets the details of the post at the given url
def get_post_details(url):
    while True:
        try:
            page = requests.get(url)
            if page.status_code != 200:
                print(page.status_code)
            soup = BeautifulSoup(page.text, "html.parser")
            title = soup.find("h1", class_="entry-title").get_text()
            content = soup.find("div", class_="td-post-content")
            paragraphs = content.find_all("p")
            text = ""
            for p in paragraphs:
                text += p.get_text() + "\n\n"
        except (ConnectionError, AttributeError):
            print(
                "Connecting error when requesting page, waiting 30 seconds before trying again..."
            )
            time.sleep(30)
            continue
        break
    return format_post(title, text)


def format_post(title, text):
    data = START_TOKEN + "\n"
    data += f"TITLE:\n\n{title}\n\n"
    data += f"TEXT:\n\n{text}"
    data += END_TOKEN + "\n"
    return data


def main():
    category = "entertainment"
    print("Getting a list of all the urls:\n")
    urls = get_article_urls(category)
    print("Complete.\n\n")
    print("Going through each article and extracting content:\n")
    # # For each post url, get the post
    # # extract the post contents, and format it correctly
    num_urls = len(urls)
    save_file = f"betootaadvocate_{category}.txt"
    if os.path.exists(save_file):
        override = str(
            input(
                "An output file for this category already exists, are you sure you want to override? (y/n): "
            )
        )
        if override == "y":
            with open(f"betootaadvocate_{category}.txt", "w") as f:
                for i, url in enumerate(urls):
                    print(f"Opening url {i}/{num_urls}: {url}\n")
                    data = get_post_details(url)
                    print("Got the data.\n")
                    f.write(data)
                    time.sleep(1 + 3 * random())
        else:
            print("\nOkay, will not override.")
    else:
        # create a new file and start writing the data
        with open(f"betootaadvocate_{category}.txt", "w") as f:
            for i, url in enumerate(urls):
                print(f"Opening url {i}/{num_urls}: {url}\n")
                data = get_post_details(url)
                print("Got the data.\n")
                f.write(data)
                time.sleep(1 + 3 * random())



main()
