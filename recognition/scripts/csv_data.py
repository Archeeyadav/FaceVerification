import os
import openai
import spacy
import requests
import pandas as pd

openai.api_key = 'sk-proj-0baKgEgeL663AmVb29FvT3BlbkFJIDaOPRnNKi8cdTeVCUpp'

# Load English language model from spaCy
nlp = spacy.load("en_core_web_lg")

def fetch_country_names():
    """
    Fetches a list of country names from restcountries API.

    Returns:
        list: A list of country names.
    """
    print("🔥 Fetching country names... 🔥")
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        country_names = [country['name']['common'] for country in data]
        print(f"Fetched {len(country_names)} country names.")
        return country_names
    else:
        print(f"Failed to fetch country names: {response.status_code}")
        return []

def analyze_text(text):
     
    country_names = fetch_country_names()
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract the names of persons and countries mentioned in the following text:\n\n{text}\n\nPersons: \nCountries: "}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    result = response.choices[0].message['content'].strip()
    
    # Process the text using spaCy NER
    doc = nlp(result)
    
    persons = set()
    countries = set()
    
    # Extract entities identified as persons or countries
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            persons.add(ent.text)
        elif ent.label_ == 'GPE' and ent.text in country_names:
            countries.add(ent.text)
    
    print(f"Extracted persons: {persons}")
    print(f"Extracted countries: {countries}")
    
    # Return the parsed result as a dictionary
    return {
        'persons': persons,
        'countries': countries
    }

if __name__ == '__main__':
    folder_path = '/face_recognition_project/Language_Data/'  
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} CSV files in folder.")
    
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"\nProcessing file: {file_name}")
        
        # Load CSV file
        df = pd.read_csv(file_path)
        
        # Assuming 'SttResult' column exists in the CSV containing the text data
        texts = df['SttResult'].tolist()
        
        print(f"Analyzing {len(texts)} text entries in {file_name}...")
        
        all_persons = set()
        all_countries = set()
        
        # Analyze each text entry and aggregate results
        for i, text in enumerate(texts, 1):
            print(f"Analyzing text {i}/{len(texts)}...")
            result = analyze_text(text)
            all_persons.update(result['persons'])
            all_countries.update(result['countries'])
        
        # Print results for the current file
        print(f"\nExample Output for {file_name}:")
        print(f"Persons: {all_persons}")
        print(f"Countries: {all_countries}")
