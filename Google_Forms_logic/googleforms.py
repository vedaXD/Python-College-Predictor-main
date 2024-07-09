import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import sys
import os


# Add the MongoDb folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '../MongoDb'))

from fetching import connect_to_mysql

# Define Google Sheets and MongoDB connection settings
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
credentials = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\Admin\Downloads\Python-College-Predictor-main\Python-College-Predictor-main\Google_Forms_logic\credentials.json',scope)
gc = gspread.authorize(credentials)

# Open a Google Sheets spreadsheet by its URL
spreadsheet_url = r'https://docs.google.com/spreadsheets/d/1TyZanm2Cut9MonuQTXgQKsN3Z9UEo4hf4adKPCBBp7Y/edit?resourcekey=&gid=1658314916#gid=1658314916'

sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.sheet1

# Get all values from the sheet
values = worksheet.get_all_values()

# Assuming the first row contains column headers
headers = values[0]
timestamp_index = headers.index('Timestamp') if 'Timestamp' in headers else None
name_index = headers.index('Name') if 'Name' in headers else None
gmail_index = headers.index('Gmail') if 'Gmail' in headers else None
score_index = headers.index('Score') if 'Score' in headers else None
category_index = headers.index('Category') if 'Category' in headers else None
preferred_courses_index = headers.index('Preferred Courses') if 'Preferred Courses' in headers else None

# Check if all required columns are found
if None in [timestamp_index, name_index, gmail_index, score_index, category_index, preferred_courses_index]:
    missing_columns = [header for header, index in zip(['Timestamp', 'Name', 'Gmail', 'Score', 'Category', 'Preferred Courses'], 
                                                       [timestamp_index, name_index, gmail_index, score_index, category_index, preferred_courses_index]) if index is None]
    raise ValueError(f"Missing columns in Google Sheet: {missing_columns}")

# Extract data for the required columns
data = []
for row in values[1:]:  # Skip the header row
    timestamp = row[timestamp_index]
    name = row[name_index]
    gmail = row[gmail_index]
    score = row[score_index]
    category = row[category_index]
    preferred_courses = row[preferred_courses_index]
    data.append({'Timestamp': timestamp, 'Name': name, 'Gmail': gmail, 'Score': score, 'Category': category, 'Preferred Courses': preferred_courses})

print("All records (Timestamp, Name, Gmail, Score, Category, Preferred Courses):")
for record in data:
    print(f"Timestamp: {record['Timestamp']}, Name: {record['Name']}, Gmail: {record['Gmail']}, Score: {record['Score']}, Category: {record['Category']}, Preferred Courses: {record['Preferred Courses']}")

# Function to establish MySQL connection
db = connect_to_mysql()

# Function to insert data into MySQL
def insert_data_to_mysql(db, data):
    cursor = db.cursor()
    for record in data:
        timestamp = record['Timestamp']
        name = record['Name']
        gmail = record['Gmail']
        score = record['Score']
        category = record['Category']
        preferred_courses = record['Preferred Courses']
        query = "INSERT INTO scores (timestamp, name, gmail, score, category, preferred_courses) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (timestamp, name, gmail, score, category, preferred_courses)
        cursor.execute(query, values)
    db.commit()
    cursor.close()

# Insert the data into MySQL
insert_data_to_mysql(db, data)
print("Data inserted into MySQL successfully.")

'''
# Function to establish MongoDB connection
def connect_to_mysql(host='mongodb+srv://vedapatki1:SEHU19yYtvbqQJ8N@cluster0.aapvwca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', port=27017, db_name='mydatabase'):
    client = MongoClient(host, port)
    db = client[db_name]
    return db

# MongoDB connection settings
db = connect_to_mysql()
collection_name = 'scores'  # Replace 'students' with your collection name
collection = db[collection_name]



#adding the data extracted from google sheet api to MongoDb server

# Function to check if a document with the same Timestamp already exists in MongoDB
def document_exists(timestamp):
    return collection.find_one({'Timestamp': timestamp}) is not None

# Insert only new data into MongoDB
new_data_to_insert = []
for record in data:
    if not document_exists(record['Timestamp']):
        new_data_to_insert.append(record)

if new_data_to_insert:
    # Insert new data into MongoDB
    result = collection.insert_many(new_data_to_insert)
    print(f"Inserted {len(result.inserted_ids)} new documents into MongoDB.")
else:
    print("No new data to insert into MongoDB.")
'''

