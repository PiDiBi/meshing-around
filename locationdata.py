# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4
from log import *

def where_am_i(lat=0, lon=0):
    whereIam = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")
    
    location = geolocator.reverse(lat + "," + lon)
    address = location.raw['address']
    address_components = ['house_number', 'road', 'city', 'state', 'postcode', 'county', 'country']
    whereIam += ' '.join([address.get(component, ', ') for component in address_components if component in address])

    grid = mh.to_maiden(float(lat), float(lon))
    whereIam += " Grid:" + grid
    
    return whereIam

def get_tide(lat=0, lon=0):
    station_id = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
    print(f"{log_timestamp()} station_lookup_url: {station_lookup_url}")
    
    try:
        station_data = requests.get(station_lookup_url, timeout=10)
        if(station_data.ok):
            station_json = station_data.json()
        else:
            return "error fetching station data"
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return "error fetching station data"

    station_id = station_json['stationList'][0]['stationId']
    

    station_url="https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id="+station_id
    print(f"{log_timestamp()} station_url: {station_url}")
    station_data = requests.get(station_url, timeout=10)
    if(station_data.ok):
        #extract table class="table table-condensed"
        soup = bs.BeautifulSoup(station_data.text, 'html.parser')
        table = soup.find('table', class_='table table-condensed')

        #extract rows
        rows = table.find_all('tr')
        #extract data from rows
        tide_data = []
        for row in rows:
            row_text = ""
            cols = row.find_all('td')
            for col in cols:
                row_text += col.text + " "
            tide_data.append(row_text)
        # format tide data into a string
        tide_string = ""
        for data in tide_data:
            tide_string += data + "\n"
        #trim off last newline
        tide_string = tide_string[:-1]
        return tide_string
                 
    else:
        return "error fetching tide data"
    
def get_weather(lat=0, lon=0):
    weather = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)
    print(f"{log_timestamp()} weather_url: {weather_url}")

    try:
        weather_data = requests.get(weather_url, timeout=10)
        if(not weather_data.ok):
            return "error fetching weather data"
    except (requests.exceptions.RequestException):
        return "error fetching weather data"

    soup = bs.BeautifulSoup(weather_data.text, 'html.parser')
    table = soup.find('div', id="detailed-forecast-body")
    #get rows
    rows = table.find_all('div', class_="row")
    
    #extract data from rows
    for index, row in enumerate(rows):
        # shrink the text
        # Define a dictionary to map the long form to the short form
        replace_dict = {
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
            "Sunday": "Sun",
            "northwest": "NW",
            "northeast": "NE",
            "southwest": "SW",
            "southeast": "SE",
            "north": "N",
            "south": "S",
            "east": "E",
            "west": "W",
            "Northwest": "NW",
            "Northeast": "NE",
            "Southwest": "SW",
            "Southeast": "SE",
            "North": "N",
            "South": "S",
            "East": "E",
            "West": "W",
            "precipitation": "precip",
            "showers": "shwrs",
            "thunderstorms": "t-storms",
            "Today": "Today: ",
            "Tonight": "Tonight: ",
            "This Afternoon": "Afternoon: "
        }

        line = row.text
        # Iterate over the dictionary and replace the long form with the short form
        for long_form, short_form in replace_dict.items():
            line = line.replace(long_form, short_form)

        #only grab a few days of weather
        
        weather += line + "\n"
        
        if index > 0:
            break
        
    #trim off last newline
    weather = weather[:-1]

    return weather