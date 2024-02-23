from bucketlist import Bucket, Matcher
from Levenshtein import ratio, jaro_winkler
from csv import DictReader, DictWriter
from unidecode import unidecode
from math import log

def first_two_letters(word):
    return unidecode(word[:2]).upper()

def transliterate(word):
    return unidecode(word)

def tokenize(row):
    row['first2'] = first_two_letters(row['name'])
    row['ascii'] = transliterate(row['name'])
    if 'name' not in row and 'city' in row:
        row['name'] = row['city']
    if 'countrycode' not in row and 'file' in row:
        row['countrycode'] = row['file']
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
    return float(1+x) / 18000000

def exact_match(x, y):
    return 1.0 if x.strip() == y.strip() else 0.0

def distance(x, y):
    return 1.0

def geoname_id(row):
    return row['geonameid']

def main():
    matcher = Matcher(must=['first2'],
                      should=[('name', jaro_winkler, 1.0),
                              ('ascii', exact_match, 0.3),
                              ('population', city_size, 0.1),
                              ('countrycode', exact_match, 0.1)])
    bucket = Bucket(matcher, 
                    tokenize, 
                    n=3, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    with open('data/search.csv') as f:
        reader = DictReader(f)
        for row in reader:
            bucket.put(row)

    city1 = {'name': 'Orbetello', 'countrycode': 'IT'}
    city2 = {'name': 'Budapesta', 'countrycode': 'RO'}
    city3 = {'name': 'Becsujhely', 'countrycode': 'HU'}
    for candidate in [city1, city2, city3]:
        candidate.update(dict(population=None))
        print('Matching', candidate)
        for city in bucket.find(candidate):
            print(city)
    
if __name__ == '__main__':
    main()