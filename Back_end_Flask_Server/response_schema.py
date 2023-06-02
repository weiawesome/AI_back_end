from typing import List

from pydantic import BaseModel

class Login_response_web(BaseModel):
    gender: str
    name: str
class Login_response_app(BaseModel):
    gender: str
    name: str
    token: str

class File_status(BaseModel):
    file_time:str
    file_id:str
    status:str
    file_type:str
class Files_response(BaseModel):
    datas: List[File_status]
class Specific_File_response(BaseModel):
    prompt:str
    content:str
    summarize:str
    details : List[str]

