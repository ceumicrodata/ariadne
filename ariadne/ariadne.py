from bucketlist import Bucket, Matcher
from Levenshtein import ratio
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
    return row

def city_size(x, y):
    return float(x) / 18000000

def distance(x, y):
    return 1.0

def geoname_id(row):
    return row['geonameid']

def main():
    matcher = Matcher(must=['first2'],
                      should=[('name', ratio, 0.7),
                              ('ascii', ratio, 1.0),
                              ('population', city_size, 0.1)])
    bucket = Bucket(matcher, 
                    tokenize, 
                    n=3, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    with open('data/search.csv') as f:
        reader = DictReader(f)
        for row in reader:
            bucket.put(row)

    city1 = {'name': 'Orbetello'}
    city2 = {'name': 'Budapesta'}
    city3 = {'name': 'Becsujhely'}
    for candidate in [city1, city2, city3]:
        candidate.update(dict(population=None))
        print('Matching', candidate)
        for city in bucket.find(candidate):
            print(city)
    
if __name__ == '__main__':
    main()