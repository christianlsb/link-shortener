from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
import pymongo
import hashlib
from hashids import Hashids
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["links"]

hashids = Hashids(salt="lsb", min_length=6)

app = FastAPI()

origins = [
   "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return 'http://127.0.0.1:8000/' + hashed

@app.get("/{keyLink}")
def get_original_link(keyLink: str):
    result = mycol.find_one({"keyLink": keyLink}, {"_id": 0, "originalLink": 1})
    print(result)
    if result:
        return RedirectResponse(url=result.get("originalLink").get("long_link"))
    else:
        return {"error": "Link not found"}
    