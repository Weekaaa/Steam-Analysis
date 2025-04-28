from lxml import html
import requests

def scrape(appid):
    # Define the URL of the website to scrape
    url = f"https://store.steampowered.com/app/{appid}/"

    # Send an HTTP request to the website and retrieve the HTML content
    response = requests.get(url)

    # Parse the HTML content using lxml
    tree = html.fromstring(response.content)

    # Extract the tag elements from the HTML tree using XPath
    xpath = "/html/body/div[1]/div[7]/div[6]/div[3]/div[3]/div[1]/div[4]/div[1]/div[2]/div[1]/div/div[4]/div[2]/div[2]/a/text()"
    link_titles = tree.xpath(xpath)

    rm = lambda x: x.strip("\n").strip("\t")
    return list(map(rm, link_titles))
