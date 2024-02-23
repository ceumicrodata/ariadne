from bucketlist import Bucket, Matcher
from Levenshtein import jaro_winkler as ratio
from csv import DictReader, DictWriter
from unidecode import unidecode
import sys

def transliterate(word):
    return unidecode(word)

def tokenize(row):
    row['ascii'] = transliterate(row['name'])
    return row

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

    writer = DictWriter(sys.stdout, fieldnames=['city1', 'geonameid1', 'country1', 'city2', 'geonameid2', 'country2'])
    writer.writeheader()

    with open('data/training-cities.csv') as f:
        reader = DictReader(f)
        for row in reader:
            row['name'] = row['city']
            for city in bucket.find(row):
                writer.writerow({'city1': row['name'], 
                                 'geonameid1': row['geonameid'], 
                                 'country1': row['file'], 
                                 'city2': city[0]['name'], 
                                 'geonameid2': city[0]['geonameid'], 
                                 'country2': city[0]['countrycode']})
        
if __name__ == '__main__':
    main()