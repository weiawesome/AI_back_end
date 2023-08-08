import os
########    ENV VARIABLE    ########
MYSQL_ADDRESS=os.environ.get("MYSQL_HOST","localhost")
MYSQL_USER=os.environ.get("MYSQL_USER","DefaultMysqlUser")
MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD","DefaultMysqlPassword")
MYSQL_DB=os.environ.get("MYSQL_DB","DefaultMysqlDb")

REDIS_ADDRESS=os.environ.get("REDIS_HOST","localhost")+":"+os.environ.get("REDIS_PORT","6379")
REDIS_HOST=os.environ.get("REDIS_HOST","localhost")
REDIS_PORT=os.environ.get("REDIS_PORT","6379")
REDIS_PASSWORD=os.environ.get("REDIS_PASSWORD","")
REDIS_DB=os.environ.get("REDIS_DB","0")

JWT_SECRET=os.environ.get("JWT_SECRET","DefaultJwtSecret")
JWT_EXPIRE_DAYS=os.environ.get("JWT_EXPIRE_DAYS","14")

PAGE_SIZE=os.environ.get("PAGE_SIZE","0")

GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID","DefaultGoogleClientId")
GOOGLE_SECRET=os.environ.get("GOOGLE_SECRET","DefaultGoogleSecret")
GOOGLE_SESSION_SECRET=os.environ.get("GOOGLE_SESSION_SECRET", "DefaultSessionSecret")

DIRECTORY_AUDIO=os.environ.get("DIRECTORY_AUDIO", "/DefaultDirectoryAudio")
DIRECTORY_GRAPH=os.environ.get("DIRECTORY_GRAPH", "/DefaultDirectoryGraph")