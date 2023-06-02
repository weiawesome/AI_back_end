import uuid
def strid2byte(id):
    str_id=str(id)
    uuid_id=uuid.UUID(str_id)
    return uuid_id.bytes
def byte2strid(id):
    uuid_id=uuid.UUID(bytes=id)
    return str(uuid_id)