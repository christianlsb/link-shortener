from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
import pymongo
import hashlib
from hashids import Hashids
from fastapi import status
 
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["links"]

hashids = Hashids(salt="lsb", min_length=6)

app = FastAPI()

class Link(BaseModel):
    long_link: str

def convert_str_for_hashid_md5(link: Link):
     md5 = hashlib.md5(link.long_link.encode()).digest()
     num = int.from_bytes(md5[:4], 'big')
     return hashids.encode(num)

@app.post("/api/shorter/")
async def create_shorter_link(link: Link):
    hashed = convert_str_for_hashid_md5(link)
    mydict = { "keyLink": hashed, "originalLink": link.model_dump() }
    x = mycol.insert_one(mydict)
    return hashed

@app.get("/api/shorter/{keyLink}")
def get_original_link(keyLink: str):
    result = mycol.find_one({"keyLink": keyLink}, {"_id": 0, "originalLink": 1})

    if result:
        return result 
    else:
        return {"error": "Link not found"}