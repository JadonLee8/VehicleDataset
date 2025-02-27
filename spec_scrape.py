from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pickle
import csv

class CarData:
    def __init__(self, car_model, car_year, msrp, horsepower, mpg, num_seats, drive_type):
        self.car_model = car_model
        self.car_year = car_year
        self.msrp = msrp
        self.horsepower = horsepower
        self.mpg = mpg
        self.num_seats = num_seats
        self.drive_type = drive_type

    def convert_to_tuple(self):
        return (self.car_model, self.car_year, self.msrp, self.horsepower, self.mpg, self.num_seats, self.drive_type)

    def __str__(self):
        return f"{self.car_model} {self.car_year} - MSRP: {self.msrp}, Horsepower: {self.horsepower}, MPG: {self.mpg}, Seats: {self.num_seats}, Drive Type: {self.drive_type}"



def main():
    cars = ['prius', 'camry', 'corolla', 'highlander', 'rav4', 'sienna', 'tacoma', 'tundra', 'supra']
    years = ['2025', '2024', '2023', '2022', '2021', '2020']

    base_url = "https://www.cars.com/research/toyota-"

    test_url = "https://www.cars.com/research/toyota-highlander-2025/specs/"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    all_car_data = []

    # Open CSV file at the start
    csv_file = open('car_specs.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    # Write header
    writer.writerow(['Model', 'Year', 'MSRP', 'Horsepower', 'MPG', 'Number of Seats', 'Drive Type'])

    for car in cars:
        for year in years:
            url = f"{base_url}{car}-{year}/specs/"

            try:
                # Fetch the page
                print("Getting url:", url)
                driver.get(url)

                # Wait for the page to load
                time.sleep(5)

                # Find the div with the class `price-amount` and get its text
                price_div = driver.find_element(By.CLASS_NAME, "price-amount")
                msrp = int(price_div.text.replace('$', '').replace(',', ''))

                model = car

                year = year

                # Locate the specific `div` containing the `svg > use` element with `xlink:href` containing "#fwd"
                key_specs = driver.find_elements(By.CLASS_NAME, "key-spec")
                drive_type = "Unknown"
                num_seats = 0
                mpg = 0
                horsepower = 0

                for spec in key_specs: #TODO: make not break for all if one is missing
                    try:
                        use_element = spec.find_element(By.CSS_SELECTOR, "svg use")
                        xlink_href = use_element.get_attribute("xlink:href")
                        if "#fwd" in xlink_href:  # Check if the string contains "#fwd"
                            drive_type = spec.find_element(By.TAG_NAME, "label").text  # Get the drive type text
                        if "#seat" in xlink_href:
                            num_seats_text = spec.find_element(By.TAG_NAME, "label").text
                            num_seats = int(num_seats_text.split()[0])
                        if "#mpg" in xlink_href:
                            mpg_text = spec.find_element(By.TAG_NAME, "label").text
                            mpg = int(''.join(filter(str.isdigit, mpg_text)))
                        if "#engine" in xlink_href:
                            horsepower_text = spec.find_element(By.TAG_NAME, "label").text
                            horsepower_text = horsepower_text.split(',')[0]
                            horsepower_text = horsepower_text.split('.')[0]
                            horsepower = float(''.join(filter(str.isdigit, horsepower_text)))
                    except:
                        continue
                
                car_data = CarData(model, year, msrp, horsepower, mpg, num_seats, drive_type)
                print("Created car data:", car_data)
                all_car_data.append(car_data)
                
                # Write car data to CSV immediately
                writer.writerow(car_data.convert_to_tuple())
                csv_file.flush()  # Ensure data is written to disk

            except Exception as e:
                print(f"An error occurred: {e}")

            # don't get flagged by cars.com
            time.sleep(5)
    
    # Close both the driver and CSV file
    driver.quit()
    csv_file.close()

    # Save to pickle file
    with open("datadb.pickle", "wb") as f:
        pickle.dump(all_car_data, f)

if __name__ == "__main__":
    main()