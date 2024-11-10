import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os.path

base_url = "https://www.mse.mk/mk/stats/symbolhistory/REPL"

today = datetime.now()

data_rows = []
flag = False

if os.path.exists("dokss.csv"):
    flagExists = True
else:
    flagExists = False


def fetch_data(code, data):
    url = f"https://www.mse.mk/mk/stats/symbolhistory/{code}/"
    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    code_data = []

    for row in rows[1:]:
        cols = row.find_all("td")
        cols = [col.text.strip() for col in cols]
        cols.append(code)  # Add the code
        code_data.append(cols)

    return code_data


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def get_codes(soup):
    codesGot = soup.find("select")
    codesGot = codesGot.text
    codesGot = codesGot.split("\n")
    filtered_codes = []
    for code in codesGot:
        if has_numbers(code):
            continue
        else:
            filtered_codes.append(code)
    return filtered_codes[:-1]


# Function to get already scraped dates from the existing data (e.g., CSV)
def get_existing_dates_from_csv():
    if os.path.exists("dokss.csv"):
        df = pd.read_csv("dokss.csv", parse_dates=["Datum"], dayfirst=True)
        return set(df["Datum"].dt.date)  # Return unique dates already scraped
    else:
        return set


# Start timing
start_time = time.time()

# Get already scraped dates
existing_dates = get_existing_dates_from_csv()


def scrape(data):
    # Send POST request to get the codes
    response = requests.post(base_url, data=data)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the codes
    codes = get_codes(soup)

    # Use multithreading to fetch data for each code
    with ThreadPoolExecutor() as executor:
        future_to_code = {executor.submit(fetch_data, code, data): code for code in codes}

        for future in as_completed(future_to_code):
            code_data = future.result()
            data_rows.extend(code_data)


for year in range(10):
    if flagExists:

        if year == 1:
            break

        dateLast = max(existing_dates)
        todayTmp = pd.to_datetime(today, format="%d.%m.%Y", errors='coerce')
        dateLast = pd.to_datetime(dateLast, format="%d.%m.%Y", errors='coerce')
        dateLast = dateLast.strftime("%d.%m.%Y")
        todayTmp = todayTmp.strftime("%d.%m.%Y")
        if dateLast != todayTmp:
            dateLast = pd.to_datetime(dateLast, format="%d.%m.%Y", errors='coerce') + timedelta(days=1)
            missing_dates = [pd.date_range(dateLast, todayTmp)]
        else:
            missing_dates = []

        if len(missing_dates) == 0:
            flag = True
            print("Nothing to scrape, all the dates are scraped!")
            break

        print(f"Scraping from {dateLast} to {todayTmp}")
        # Prepare the data for the POST request
        data = {
            'FromDate': dateLast,
            'ToDate': todayTmp
        }

        scrape(data)

    else:
        from_date = (today - timedelta(days=365 * (year + 1))).date()
        to_date = (today - timedelta(days=365 * year)).date()

        print(f"Scraping from {from_date} to {to_date}")

        data = {
            'FromDate': from_date,
            'ToDate': to_date
        }

        scrape(data)

# Create DataFrame and save to CSV
if flag:
    df = pd.read_csv("dokss.csv", parse_dates=["Datum"], dayfirst=True)
else:
    if flagExists:
        df1 = pd.read_csv("dokss.csv", parse_dates=["Datum"], dayfirst=True)

        if len(data_rows) > 0:
            df = pd.DataFrame(data_rows)
            df.columns = ['Datum', 'Cena na posledna transakcija', 'Mak.', 'Min.', 'Prosecna cena', '%prom', 'Kolicina',
                          'Promet vo BEST vo denari', 'Vkupen promet vo denari', 'Ime na Kompanija']

            df = pd.concat([df1, df], ignore_index=True, axis=0)
        else:
            df = df1
    else:
        df = pd.DataFrame(data_rows)

df.columns = ['Datum', 'Cena na posledna transakcija', 'Mak.', 'Min.', 'Prosecna cena', '%prom', 'Kolicina',
              'Promet vo BEST vo denari', 'Vkupen promet vo denari', 'Ime na Kompanija']


# Strip any leading/trailing whitespace in the "Datum" column
df["Datum"] = df["Datum"].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Convert the "Datum" column to datetime format with Macedonian date format (day-month-year)
df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors='coerce')

# Sort the DataFrame by "Ime na Kompanija" and "Datum" (latest dates first)
df.sort_values(by=["Ime na Kompanija", "Datum"], ascending=[True, False], inplace=True)

# Print and save to CSV with date format "day-month-year" (e.g., 07-11-2024)
print(df)
df.to_csv("dokss.csv", index=False, date_format="%d-%m-%Y")

# End timing and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time taken to execute: {elapsed_time:.2f} seconds")
