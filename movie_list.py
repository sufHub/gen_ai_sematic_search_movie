
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests

uri = "mongodb+srv://shaikummer:<password>@cluster0.tt76oit.mongodb.net/?retryWrites=true&w=majority"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
hf_token = "<hf_token>"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def generate_embedding_from_hugging_face(text: str) -> list[float]:
    response = requests.post(
    embedding_url,
    headers={"Authorization": f"Bearer {hf_token}"},
    json={"inputs": text})

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()

def createEmbeddingsForMongoDB(collection):
      
    for doc in collection.find({'plot' :{"$exists": True}}).limit(50):
     doc['plot_embedding_hf'] = generate_embedding_from_hugging_face(doc['plot'])
     collection.replace_one({'_id': doc['_id']}, doc)

try:
    client.admin.command('ping')
    db = client.sample_mflix
    collection = db.movies

    #createEmbeddingsForMongoDB(collection)

    query = "a boy who loves his country"

    results = collection.aggregate([
        {"$vectorSearch": {
        "queryVector": generate_embedding_from_hugging_face(query),
        "path" : "plot_embedding_hf",
        "numCandidates": 100,
        "limit": 4,
        "index": "PlotSemanticSearch",
	    }}
    ]);

    for document in results:
      print(f'Movie name: {document["title"]}, \nMovie Plot: {document["plot"]}\n')

except Exception as e:
    print(e)

