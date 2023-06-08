from typing import List

from pydantic import BaseModel
class Login_response_app(BaseModel):
    token: str

class File_status(BaseModel):
    file_time:str
    file_id:str
    status:str
    file_type:str
class Files_response(BaseModel):
    total_pages: int
    current_page: int
    datas: List[File_status]
class Specific_File_response(BaseModel):
    prompt:str
    content:str
    summarize:str
    details : List[str]
class Information_response(BaseModel):
    name:str
    gender:str
    mail:str

