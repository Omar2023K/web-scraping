from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
import re
import time


path = 'C:/Users/omar5/OneDrive/Desktop/vscode/chromedriver.exe'

service = Service(executable_path=path)
options = Options()



driver = webdriver.Chrome(options=options, service=service)

options.add_experimental_option(name='detach', value=True)

driver.get('https://www.akbw.de/kammer/datenbanken/bueroverzeichnis-architektenprofile/suchergebnisse-architektenprofile?tx_fufbueroprofile_pi1%5BmaxPerPage%5D=100')

try:
    configure_button_xpath = '//button[contains(@class,"fc_button fc_button_primary s-bg")]'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, configure_button_xpath))).click()
except Exception as e:
    print(f"Cookie configuration button click failed: {e}")

companies_xpath = '//div[contains(@class,"inside-content search-results")]//span[contains(@class,"read-more link-fix-y")]/a'
companies = driver.find_elements(By.XPATH, companies_xpath)
companies_link = [com.get_attribute("href") for com in companies]

# companies = []
# for com_link in companies_link:
#     companies.append(com_link)


# Function to extract company links and track the page number
def extract_companies_from_page(page_number):
    companies_xpath = '//div[contains(@class,"inside-content search-results")]//span[contains(@class,"read-more link-fix-y")]/a'
    companies = driver.find_elements(By.XPATH, companies_xpath)
    companies_link = [com.get_attribute("href") for com in companies]
    
    # Add the page number to each company link to track which page it's from
    companies_with_page = [(link, page_number) for link in companies_link]
    
    return companies_with_page

# Initialize empty list to store all companies
all_companies = []

# Loop through multiple pages
page_number = 1

while True:
    # Extract companies from the current page
    companies = extract_companies_from_page(page_number)
    all_companies.extend(companies)
    
    # Check if there's a "next" button and if it's clickable
    try:
        # Look for the next page button (using a more general XPath in case it's dynamic)
        next_button_xpath = "(//a[contains(@class,'page-link')])[4]"  # Adjust XPath based on actual page structure
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_button_xpath)))
        
        # Click on the next button
        next_button.click()
        
        # Wait for the page to load after clicking "Next"
        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))  # Wait until the next page loads
        
        page_number += 1  # Increment the page number for the next page
        time.sleep(2)  # Optional: sleep for a short period before loading the next page
        
    except Exception as e:
        print(f"Next button not found or failed to click: {e}")
        break

# Convert the list of companies into a DataFrame (optional)
df = pd.DataFrame(all_companies, columns=["Company Link", "Page Number"])

# Print the DataFrame (or save it to a file, if needed)
print(df)

# Optionally, save to a CSV file
# df.to_csv('companies.csv', index=False)

# Close the browser once the scraping is done



len(all_companies)

# Define empty lists to store company data
company_name = []
web = []
phone = []
address = []
email = []
zip_and_city = []
phone_regex = r'(\+?\d[\d\s-]{6,})'

# Loop through each company link in companies_link
for com_link, page_number in all_companies:
    try:
        print(f"Scraping page {page_number}")

        driver.get(com_link)  # Navigate to the company page

        # Wait for the title to be visible on the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"archProfTitle")]/h2'))
        )

        # Scraping logic for the company
        try:
            title = driver.find_element(By.XPATH, '//div[contains(@class,"archProfTitle")]/h2').text
        except Exception as e:
            print(f"Error extracting title: {e}")
            title = np.nan
        company_name.append(title)

        # Scrape website
        try:
            web_link = driver.find_element(By.XPATH, "//div[contains(@class,'archProfSidebarKontakt')]//p[b[text()='Web:']]/a[2]").text
        except:
            web_link = np.nan
        web.append(web_link)

        # Scrape phone number
        try:
            phone_a = driver.find_element(By.XPATH, "//div[contains(@class,'archProfSidebarKontakt')]//p[b[text()='Tel.:']]")
            phone_text = phone_a.text.strip()  
            phone_match = re.search(phone_regex, phone_text)
            if phone_match:
                phone_number = phone_match.group(1).strip()
            else:
                phone_number = np.nan  
        except Exception as e:
            phone_number = np.nan
        phone.append(phone_number)


        # Scrape address
        try:
            address_text = driver.find_element(By.XPATH, "//div[@class='archProfSidebarKontakt']/p[1]").text.strip()
            lines = address_text.split('\n')
            # Ensure address format is consistent (check for 'nan' in extracted lines)
            address_1 = lines[1].strip() if len(lines) > 1 and lines[1].strip() != 'nan' else np.nan
            address_2 = lines[2].strip() if len(lines) > 2 and lines[2].strip() != 'nan' else np.nan
            address_a = f"{address_1} {address_2}" if address_1 and address_2 else np.nan
        except Exception as e:
            address_a = np.nan
        address.append(address_a)

        # Scrape email
        try:
            email_a = driver.find_element(By.XPATH, "//div[contains(@class,'archProfSidebarKontakt')]//p[b[text()='E-Mail:']]/a").text.strip()
        except Exception as e:
            email_a = np.nan
        email.append(email_a)

        # Scrape zip and city
        try:
            zipcode_and_c = driver.find_element(By.XPATH, '//div[contains(@class,"archProfSidebarKontakt")]/p[1]').text.strip()
            lines = zipcode_and_c.split('\n')
            # Handling zip and city based on structure
            zipcode_and_c = lines[3].strip() if len(lines) > 3 else (lines[2].strip() if len(lines) > 2 else np.nan)
        except Exception as e:
            zipcode_and_c = np.nan
        zip_and_city.append(zipcode_and_c)

    except Exception as e:
        print(f"Error scraping company {com_link}: {e}")
        # In case of error, ensure NaN values are added for consistency
        company_name.append(np.nan)
        web.append(np.nan)
        phone.append(np.nan)
        address.append(np.nan)
        email.append(np.nan)
        zip_and_city.append(np.nan)
        continue  # Skip to the next company if there's an error

# Check if all lists have the same length
list_lengths = [len(company_name), len(web), len(phone), len(address), len(email), len(zip_and_city)]
print(f"Lengths of all lists: {list_lengths}")

# Convert the data into a DataFrame (optional)
company_data = pd.DataFrame({
    'Company Name': company_name,
    'Website': web,
    'Phone': phone,
    'Address': address,
    'Email': email,
    'Zip and City': zip_and_city,
})

# Print the DataFrame (or save it to a file if needed)
print(company_data)

# Optionally, save to a CSV file
company_data.to_csv('company_data.csv', index=False)

# Close the browser once scraping is done
driver.quit()
