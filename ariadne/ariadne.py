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

LANGUAGES = {'HU': 'hu',
             'AT': 'de',
             'DE': 'de',
             'PL': 'pl',
             'SK': 'sk',
             'RO': 'ro',
             'GR': 'el',
             'TR': 'tr',
             'XX': 'en',
             'b': 'en'}

STOPWORDS = {'AT': ['G', ]}
ABBREVIATIONS = {'AT': [
    ('St', 'Sankt'),
    ('D', 'Deutschland'),
    ('BRD', 'Deutschland'),
    ('Sbg', 'Salzburg'),
    ('Ktn', 'Kärnten'),
    ('Stmk', 'Steiermark'),
    ('NÖ', 'Niederösterreich'),
    ('OÖ', 'Oberösterreich'),
    ('W', 'Wien'),
    ('Klgft', 'Klagenfurt'),
    ('CH', 'Schweiz'),
    ('CZ', 'Tschechien'),
    ('TR', 'Türkei'),
    ('eh', 'ehemalige'),
    ],
    'DE': [
    ('St', 'Sankt'),
    ('D', 'Deutschland'),
    ('BRD', 'Deutschland'),
    ('Sbg', 'Salzburg'),
    ('Ktn', 'Kärnten'),
    ('NÖ', 'Niederösterreich'),
    ('OÖ', 'Oberösterreich'),
    ('W', 'Wien'),
    ('Klgft', 'Klagenfurt'),
    ('CH', 'Schweiz'),
    ('CZ', 'Tschechien'),
    ('TR', 'Türkei'),
    ('eh', 'ehemalige'),
    ]}

# 1-gram of all ascii letters included in the name, 1 bit for each, resulting in a 32-bit integer
def ascii_signature(word):
    signature = 0
    for c in word:
        if c.isalpha():
            signature |= 1 << (ord(c) - 65) if c.isupper() else 1 << (ord(c) - 97)
    return signature

# how many bits are different between the two signatures
def distance_signature(x, y):
    return bin(x ^ y).count('1')

# unit circle around the signature, returning all signatures within a distance of 1
def signature_circle(signature):
    return [signature ^ (1 << i) for i in range(32)]

def first_two_letters(word):
    return unidecode(word[:2]).upper()

def transliterate(word):
    return unidecode(word)

def nornalize_name(name):
    name = name.lower().strip()
    REMOVE = ['/', '.', ',', '-']
    STOP = '('
    if STOP in name:
        return name[0:name.index(STOP)]
    return ' '.join(''.join([' ' if c in REMOVE else c for c in name]).split())

def analyze(row):
    return row

def preprocess(row):
    row['name'] = nornalize_name(row['name'])
    row['first2'] = first_two_letters(row['name'])
    row['ascii'] = transliterate(row['name'])
    row['signature'] = ascii_signature(row['ascii'])
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
        row['country'] = 'XX'
    if 'isolanguage' in row:
        row['language'] = row['isolanguage']
    else:
        row['language'] = LANGUAGES[row['country']]
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

def country_match(x, y):
    if (x.lower() == y.lower()) | (x.lower() in y.lower()) | (y.lower() in x.lower()):
        return 1.0
    return 0.0

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

def create_bucket(fname, scoring):
    exact_signature = Bucket(
        Matcher(must=['signature'],
                should=scoring),
                    analyze, 
                    n=1, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    first_letters = Bucket(Matcher(must=['first2'],
                    should=scoring), 
                    analyze, 
                    n=1, # how many hits to return 
                    group_by=geoname_id # only return one result by geonameid 
                    )
    with open(fname) as f:
        reader = DictReader(f)
        for row in reader:
            row = preprocess(row)
            exact_signature.put(row)
            first_letters.put(row)
    return (exact_signature, first_letters)

if __name__ == '__main__':
    reader = DictReader(sys.stdin)
    writer = DictWriter(sys.stdout, 
                        fieldnames=[
                            'city1',
                            'country1',
                            'geonameid2',
                            'city2',
                            'country2',
                            'language2',
                            'score'])
    
    writer.writeheader()
    print('Creating buckets...', file=sys.stderr)
    scoring = [('name', jaro_winkler, 0.67),
                ('name', ratio, 0.33),
                ('ascii', exact_match, 0.1),
                ('population', city_size, 0.1),
                ('country', exact_match, 0.06),
                ('language', exact_match, 0.14),
                ('location', proximity, 0.1)]
    exact_signature, first_letters = create_bucket('data/search.csv', scoring)
    print('Matching...', file=sys.stderr)
    for row in reader:
        row['name'] = row['Birthplace']
        row['countrycode'] = row['Country']
        row = preprocess(row)
        # try exact match first
        results = exact_signature.find(row)
        if not results:
            # if no exact match, try first two letters
            results = first_letters.find(row)
        if results:
            city = results[0]
            writer.writerow({'city1': row['Birthplace'], 
                                'country1': row['Country'],
                                'geonameid2': city[0]['geonameid'],
                                'city2': city[0]['name'].title(), 
                                'country2': city[0]['country'],
                                'language2': city[0]['language'],
                                'score': city[1]})