from bucketlist import Bucket, Matcher
from Levenshtein import jaro_winkler, ratio, distance as levenshtein
from csv import DictReader, DictWriter
from unidecode import unidecode
import sys
import math

def haversine(coord1, coord2):
    # Earth radius in kilometers
    R = 6371.0

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

def transliterate(word):
    return unidecode(word)

def first_two_letters(word):
    return unidecode(word[:2]).upper()

def tokenize(row):
    row['first2'] = first_two_letters(row['name'])
    row['ascii'] = transliterate(row['name'])
    if ('latitude' in row) and ('longitude' in row) and (row['latitude'] != '') and (row['longitude'] != ''):
        row['location'] = (float(row['latitude']), float(row['longitude']))
    else:
        row['location'] = None
    if 'countrycode' in row:
        row['country'] = row['countrycode']
    else:
        row['country'] = None
    if ('population' in row) and (row['population'] != '') and (row['population'] is not None):
        row['population'] = float(row['population'])
    else:
        row['population'] = None
    return row

def city_size(x, y):
    return math.log((1+x) / 18000000)

def distance(x, y):
    return -haversine(x, y) 

def geoname_id(row):
    return row['geonameid']

def bad_match(x, y):
    return x == y if 0.0 else 1.0

def main():
    matcher = Matcher(must=[],
                      should=[('ascii', ratio, 1.0),
                            ('name', ratio, 0.5)],
                      stone_geary=0.2)
    bucket = Bucket(matcher, 
                    tokenize, 
                    n=5, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    with open('data/search.csv') as f:
        reader = DictReader(f)
        for row in reader:
            bucket.put(row)

    writer = DictWriter(sys.stdout, fieldnames=['city1', 'geonameid1', 'country1', 'city2', 'geonameid2', 'country2', 'ascii_ratio', 'name_ratio', 'name_jaro', 'name_levenshtein', 'size2', 'same_country'])
    writer.writeheader()

    with open('data/training-cities.csv') as f:
        reader = DictReader(f)
        for row in reader:
            row['name'] = row['city']
            row['countrycode'] = row['file']
            for city in bucket.find(row):
                x = tokenize(row)
                y = tokenize(city[0])
                writer.writerow({'city1': row['name'], 
                                 'geonameid1': row['geonameid'], 
                                 'country1': row['file'], 
                                 'city2': city[0]['name'], 
                                 'geonameid2': city[0]['geonameid'],
                                 'country2': city[0]['countrycode'],
                                 'ascii_ratio': ratio(x['ascii'], y['ascii']),
                                 'name_ratio': ratio(x['name'], y['name']),
                                 'name_jaro': jaro_winkler(x['name'], y['name']),
                                 'name_levenshtein': levenshtein(x['name'], y['name']),
                                 'size2': city_size(y['population'], y['population']),
                                 'same_country': 1 if x['country'] == y['country'] else 0
                                })
        
if __name__ == '__main__':
    main()