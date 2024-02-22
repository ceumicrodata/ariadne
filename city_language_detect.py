import pandas as pd
from langdetect import detect

# Read the dataset
df = pd.read_stata(r'C:\Users\depir\OneDrive\Desktop\Geodata\geoname_split1.dta')

# Function to detect the language
def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        print("Error detecting language for text:", text)
        print("Error message:", e)
        return "Unknown"

# Apply language detection to each row
df['language'] = df['split_var'].apply(detect_language)

# Export the DataFrame to a CSV file
df.to_csv('language_detection_results.csv', index=False)
