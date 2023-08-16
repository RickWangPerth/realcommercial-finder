from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.realcommercial.com.au/for-lease/industrial-warehouse/?includePropertiesWithin=includesurrounding&keywords=Gantry%2BCrane&locations=perth-greater-region-wa%2Cdarwin-greater-region-nt&minFloorArea=400&page="
DOMAIN = "https://www.realcommercial.com.au"

def get_links_from_page(url):
    # Fetch the page content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return []

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the relevant anchor tags
    property_links = soup.find_all('a', href=True, tabindex="-1")

    # Extract the href attribute (i.e., the link) from each anchor tag, ensuring it starts with /for-lease/
    # and prefix the domain to the URL
    return [DOMAIN + link['href'] for link in property_links if link['href'].startswith('/for-lease/')]

urls = []
for page_number in range(1, 7):  # for pages 1 through 6
    page_url = BASE_URL + str(page_number)
    urls.extend(get_links_from_page(page_url))


def extract_agent_details(driver, url):  # pass the driver instance to the function
    try:
        driver.get(url)

        # Wait for the contact number button to load
        wait = WebDriverWait(driver, 10)
        contact_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "AgentDetails_button_1SE0f")))

        # Using JavaScript to click the contact button
        driver.execute_script("arguments[0].click();", contact_button)

        # Wait and extract the contact number
        contact_number_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.AgentDetails_button_1SE0f span")))
        contact_number = contact_number_element.text.strip()

        # Find the agent's name from the page content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        agent_name_tag = soup.find("h4", class_="AgentDetails_name_23QWU")
        agent_name = agent_name_tag.text.strip() if agent_name_tag else "Agent Name not found"

        return agent_name, contact_number

    except Exception as e:
        print(f"Error retrieving agent details for {url}. Error: {e}")
        return "Error", "Error"


# Function to extract price information from the HTML
def extract_price(html):
    price_tag = html.find("p", class_="PriceGroup_priceGroup_2W4BV")
    if price_tag:
        return price_tag.text.strip()
    return "Price not found"

# Function to extract floor area information from the HTML
def extract_floor_area(html):
    floor_area_tags = html.find_all("div", class_="Attribute_attribute_3lq_3")
    for tag in floor_area_tags:
        label = tag.find("p", class_="Attribute_label_1bYjg")
        if label and "Floor area" in label.text:
            return tag.find("p", class_="Attribute_value_i8Dee").text.strip()
    return "Floor area not found"

# Function to extract land area information from the HTML
def extract_land_area(html):
    land_area_tags = html.find_all("div", class_="Attribute_attribute_3lq_3")
    for tag in land_area_tags:
        label = tag.find("p", class_="Attribute_label_1bYjg")
        if label and "Land area" in label.text:
            return tag.find("p", class_="Attribute_value_i8Dee").text.strip()
    return "Land area not found"

# Function to extract address information from the URL
def extract_address_from_url(url):
    # Get the part of the URL after 'property-' and before the last dash and the state
    address = url.split("/property-")[-1].rsplit('-', 1)[0]
    return address.replace('-', ' ')

# Function to extract state information from the address
def extract_state_from_address(address):
    # The state abbreviation is the second to last word in the address
    return address.split()[-2].upper()

# Function to feature information from the URL
def extract_feature(html):
    headline_tag = html.find("h2", class_="PrimaryDetailsBottom_headline_3oTbK")
    
    # Extract the description and replace <br> and <br/> with newline characters
    description_tag = html.find("div", class_="DescriptionPanel_description_20faq")
    if description_tag:
        for br in description_tag.find_all("br"):
            br.replace_with("\n")
    
    headline = headline_tag.text.strip() if headline_tag else ""
    description = description_tag.text.strip() if description_tag else ""
    
    return f"{headline}\n{description}"

# Create an empty list to store data
data = []

# Initialize the Selenium webdriver before the loop
options = Options()
options.add_argument('--headless')  # Run Chrome in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
chrome_prefs = {}
chrome_prefs["profile.default_content_setting_values"] = {"images": 2}
options.experimental_options["prefs"] = chrome_prefs
driver = webdriver.Chrome(options=options)

# Loop through the URLs and crawl information
for index, url in enumerate(urls, start=1): 
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        floor_area = extract_floor_area(soup).replace("m²", "m2")  # Replace special character
        land_area = extract_land_area(soup).replace("m²", "m2")    # Replace special character
        price = extract_price(soup)
        address = extract_address_from_url(url)
        state = extract_state_from_address(address)
        feature = extract_feature(soup)  # Extract the feature (description)
        agent_name, contact_number = extract_agent_details(driver, url)
        data.append([index, address, state, price, floor_area, land_area, feature, agent_name, contact_number, url])
        time.sleep(2)

# Make sure to close the Selenium webdriver instance after you're done
driver.quit()

# Create a pandas DataFrame
df = pd.DataFrame(data, columns=["No.", "Address", "State", "Price", "Floor Area", "Land Area", "Feature", "Agent Name", "Contact Number", "URL"])

# Export the DataFrame to a CSV file
df.to_csv("property_data.csv", index=False)
