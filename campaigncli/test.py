import requests
from dotenv import load_dotenv
from pinecone import Pinecone , ServerlessSpec
import os
from bs4 import BeautifulSoup
load_dotenv()
CERT_FILE = "cognizant_root.pem"
base_link = "https://experienceleague.adobe.com/en/docs/campaign-classic/using/campaign-classic-home"

# soup = BeautifulSoup(requests.get(base_link).content, "html.parser")
# res = soup.find("div" , attrs={"class":"toc-tree"})
# print(res)

try:
    # 1. Test Management API (Control Plane)
    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
    )
    print("Testing Management API...")
    indexes = pc.list_indexes()
    print("✅ Successfully connected to Pinecone Management API!")
    # 2. Test Data API (Data Plane)
    # Note: Replace 'my-rag-index' with your actual index name
    index = pc.Index("my-rag-index")
    stats = index.describe_index_stats()
    print("✅ Successfully connected to your Index!")
    print(f"Index Stats: {stats}")

except Exception as e:
    print(f"❌ Connection Failed: {e}")