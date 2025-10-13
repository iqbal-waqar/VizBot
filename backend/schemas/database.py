from pydantic import BaseModel
from typing import Optional, Literal


class PostgreSQLConnection(BaseModel):
    host: str
    port: int = 5432
    database: str
    username: str
    password: str


class MongoDBConnection(BaseModel):
    host: str
    port: int = 27017
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"


class DatabaseConnectionRequest(BaseModel):
    db_type: Literal["postgresql", "mongodb"]
    postgresql_config: Optional[PostgreSQLConnection] = None
    mongodb_config: Optional[MongoDBConnection] = None
