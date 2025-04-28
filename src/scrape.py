from lxml import html
import requests

def scrapeTags(appid, global_vars):
    logger = global_vars.logger
    # Define the URL of the website to scrape
    url = f"https://store.steampowered.com/app/{appid}/"

    # Send an HTTP request to the website and retrieve the HTML content
    response = requests.get(url)

    if response.status_code != 200: 
        logger.error(f"Failed to fetch Tags using Scraping for appid {appid}, html status_code: {response.status_code}")
        return "Cannot Fetch Tags"
        
    logger.info(f"fetched tags for appid: {appid}")
    
    # Parse the HTML content using lxml
    tree = html.fromstring(response.content)

    # Extract the tag elements from the HTML tree using XPath
    xpath = "/html/body/div[1]/div[7]/div[6]/div[3]/div[3]/div[1]/div[4]/div[1]/div[2]/div[1]/div/div[4]/div[2]/div[2]/a/text()"
    link_titles = tree.xpath(xpath)

    # lambda function to remove trailing new line and tabs from each tag
    rm = lambda x: x.strip("\n").strip("\t")

    return list(map(rm, link_titles))
