""" Module to scrape the web page of the project """

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time, csv, os, configparser
import numpy as np
from utils.utils import obtain_CA_and_Province

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config/config.ini")
config.read(config_path)

# Read configuration
INITIAL_LATITUDE = config.getfloat("Coordinates", "INITIAL_LATITUDE")
INITIAL_LONGITUDE = config.getfloat("Coordinates", "INITIAL_LONGITUDE")
FINAL_LATITUDE = config.getfloat("Coordinates", "FINAL_LATITUDE")
FINAL_LONGITUDE = config.getfloat("Coordinates", "FINAL_LONGITUDE")
GECKODRIVER_PATH = config.get("Paths", "GECKODRIVER_PATH")
WEB_PAGE_PATH = config.get("Paths", "WEBSCRAPING_PAGE_PATH")
OUTPUT_PATH = config.get("Paths", "WEBSCRAPING_OUTPUT_PATH")

# Firefox options
firefox_options = Options()
firefox_options.headless = False

# Firefox service
service = Service(os.path.join(os.path.dirname(__file__), GECKODRIVER_PATH))
driver = webdriver.Firefox(service=service, options=firefox_options)

# Open the web page
driver.get(WEB_PAGE_PATH)

# Wait for the page to load
time.sleep(4)

# Find the elements
for lat in np.arange(INITIAL_LATITUDE, FINAL_LATITUDE, 0.25):
    for lon in np.arange(INITIAL_LONGITUDE, FINAL_LONGITUDE, 0.25):
        # Round the latitude and longitude to 3 decimal places
        lat = round(lat, 3)
        lon = round(lon, 3)

        # Find the input latitude by ID and send the latitude
        input_lat = driver.find_element(By.ID, "inputLat")
        input_lat.clear()
        input_lat.send_keys(str(lat))

        # Find the input longitude by ID and send the longitude
        input_lon = driver.find_element(By.ID, "inputLon")
        input_lon.clear()
        input_lon.send_keys(str(lon))

        # Wait for the page to load
        time.sleep(1)

        try:
            driver.find_element(By.ID, "btninputLatLon").click()
            time.sleep(2)
            # Simulate the click on the "Visualize" button
            visualize = driver.find_element(By.ID, "btviewPVGridGraph")
            driver.execute_script("arguments[0].click();", visualize)

            # Wait for the page to load
            time.sleep(2)

            no_data = driver.find_element(By.ID, "tr_nodata")
            print("No data")
        except:  # If there is no no_data element in the page
            # Find the element that contains the graph
            graph = driver.find_element(By.CLASS_NAME, "highcharts-series-group")

            # Create an action chain
            action = ActionChains(driver)

            # Find all the rectangles in the graph
            rectangulos = graph.find_elements(By.TAG_NAME, "rect")

            # Iterate over the rectangles
            for rect in rectangulos:
                try:
                    # Move the mouse to the rectangle
                    action.move_to_element(rect).perform()

                    # Extract the tooltip text
                    tooltip = driver.find_element(By.CLASS_NAME, "highcharts-tooltip")
                    tooltip_text = tooltip.text

                    # Obtain the autonomous community and the province
                    comunidad_autonoma, municipio = obtain_CA_and_Province(lat, lon)

                    # Write the data to a CSV file
                    with open(OUTPUT_PATH, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            [
                                lat,
                                lon,
                                tooltip_text,
                                comunidad_autonoma,
                                municipio,
                            ]
                        )
                    time.sleep(0.2)
                except:
                    continue

# Close the driver
driver.quit()
