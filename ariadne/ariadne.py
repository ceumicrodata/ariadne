from bucketlist import Bucket, Matcher
from Levenshtein import ratio, jaro_winkler
from csv import DictReader, DictWriter
from unidecode import unidecode
import sys
import math

CAPITALS = {'HU': (47.49835, 19.04045),
            'AT': (48.20849, 16.37208),
            'DE': (52.52437, 13.41053),
            'PL': (52.22977, 21.01178),
            'SK': (48.14816, 17.10674),
            'RO': (44.42677, 26.10254),
            'GR': (37.97945, 23.71622),
            'TR': (41.00824, 28.97836)}

def first_two_letters(word):
    return unidecode(word[:2]).upper()

def transliterate(word):
    return unidecode(word)

def nornalize_name(name):
    name = name.lower().strip()
    REMOVE = ['/', '.', ',']
    STOP = '('
    if STOP in name:
        return name[0:name.index(STOP)]
    return ' '.join(''.join([' ' if c in REMOVE else c for c in name]).split(' '))

def tokenize(row):
    row['name'] = nornalize_name(row['name'])
    row['first2'] = first_two_letters(row['name'])
    row['ascii'] = transliterate(row['name'])
    if 'name' not in row and 'city' in row:
        row['name'] = row['city']
    if 'countrycode' not in row and 'file' in row:
        row['countrycode'] = row['file']
    if ('latitude' in row) and ('longitude' in row) and (row['latitude'] != '') and (row['longitude'] != ''):
        row['location'] = (float(row['latitude']), float(row['longitude']))
    elif 'countrycode' in row and row['countrycode'] in CAPITALS:
        row['location'] = CAPITALS[row['countrycode']]
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
    if x is None:
        return 0.65
    else:
        return math.sqrt(0.65 + x / 18000000.0)

def exact_match(x, y):
    return 1.0 if x.strip() == y.strip() else 0.0

def proximity(x, y):
    if x is None or y is None:
        return 0.65
    return math.exp(-0.02*haversine(x, y))

def geoname_id(row):
    return row['geonameid']

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

def create_bucket(fname):
    matcher = Matcher(must=['first2'],
                      should=[('name', jaro_winkler, 0.67),
                              ('name', ratio, 0.33),
                              ('ascii', exact_match, 0.1),
                              ('population', city_size, 0.1),
                              ('countrycode', exact_match, 0.05),
                              ('location', proximity, 0.1)])
    bucket = Bucket(matcher, 
                    tokenize, 
                    n=1, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    with open(fname) as f:
        reader = DictReader(f)
        for row in reader:
            bucket.put(row)
    return bucket

if __name__ == '__main__':
    reader = DictReader(sys.stdin)
    writer = DictWriter(sys.stdout, 
                        fieldnames=[
                            'city1',
                            'country1',
                            'geonameid2',
                            'city2',
                            'country2',
                            'score'])
    
    writer.writeheader()
    bucket = create_bucket('data/search.csv')
    for row in reader:
        row['name'] = row['Birthplace']
        row['countrycode'] = row['Country']
        results = bucket.find(row)
        if results:
            city = results[0]
            writer.writerow({'city1': row['Birthplace'], 
                                'country1': row['Country'],
                                'geonameid2': city[0]['geonameid'],
                                'city2': city[0]['name'], 
                                'country2': city[0]['countrycode'],
                                'score': city[1]})