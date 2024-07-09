import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import mysql.connector

# Function to establish MongoDB connection
def connect_to_mysql():
    return mysql.connector.connect(
        host='veda1.mysql.pythonanywhere-services.com',
        user='veda1',
        password='Database1234',  # Your MySQL password
        database='veda$scores'
    )

# Connect to MongoDB
db = connect_to_mysql()
collection_name = 'scores'
collection = db[collection_name]
last_processed_collection = 'last_processed'
last_processed_db = db[last_processed_collection]

def insert_data_to_mysql(db, data):
    cursor = db.cursor()
    
    for record in data:
        cursor.execute('''
            INSERT INTO scores (Timestamp, Name, Gmail, Score, Category, Preferred_Courses)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Name = VALUES(Name),
                Gmail = VALUES(Gmail),
                Score = VALUES(Score),
                Category = VALUES(Category),
                Preferred_Courses = VALUES(Preferred_Courses)
        ''', (record['Timestamp'], record['Name'], record['Gmail'], record['Score'], record['Category'], record['Preferred Courses']))
    
    db.commit()
    cursor.close()

def fetch_specific_fields(db, last_processed_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM scores
        WHERE id > %s
        ORDER BY id ASC
    ''', (last_processed_id,))
    
    raw_data = cursor.fetchall()
    
    for record in raw_data:
        if 'Score' in record:
            record['Score'] = int(record['Score'])
        if 'Preferred_Courses' in record:
            if isinstance(record['Preferred_Courses'], str):
                record['Preferred_Courses'] = record['Preferred_Courses'].strip("[]").split(',')
                record['Preferred_Courses'] = [course.strip() for course in record['Preferred_Courses']]
    
    cursor.close()
    return raw_data

def get_last_processed_id(db):
    cursor = db.cursor()
    cursor.execute('SELECT last_processed_id FROM last_processed LIMIT 1')
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else '0'  # Default to '0' if no record found

def update_last_processed_id(db, last_processed_id):
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO last_processed (last_processed_id)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE
            last_processed_id = VALUES(last_processed_id)
    ''', (last_processed_id,))
    db.commit()
    cursor.close()



















'''
# Function to update the last processed record's ObjectId
def update_last_processed_id(last_processed_id):
    last_processed_db.update_one({}, {'$set': {'last_processed_id': last_processed_id}}, upsert=True)

# Fetch specific fields from MongoDB
fields_to_fetch = ['Name', 'Gmail', 'Score', 'Category', 'Preferred Courses']
last_processed_id = get_last_processed_id()
fetched_data = fetch_specific_fields(db, collection_name, fields_to_fetch, last_processed_id)

print("Fetched data from MongoDB:")
for record in fetched_data:
    print(record)
'''