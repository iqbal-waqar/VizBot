import pandas as pd
from langchain_core.tools import tool
from typing import Dict, Any
import json
from pymongo import MongoClient
from sqlalchemy import create_engine, inspect
import traceback


@tool
def explore_postgresql_database(connection_string: str) -> str:
    """Explore PostgreSQL database schema and get table information.
    
    Args:
        connection_string: PostgreSQL connection string
    
    Returns:
        JSON string with database schema information
    """
    try:
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        result = {
            "tables": [],
            "total_tables": 0
        }
        
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column['name'],
                    "type": str(column['type']),
                    "nullable": column.get('nullable', True)
                })
            
            result["tables"].append({
                "name": table_name,
                "columns": columns,
                "column_count": len(columns)
            })
        
        result["total_tables"] = len(result["tables"])
        engine.dispose()
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


@tool
def query_postgresql_table(connection_string: str, table_name: str, limit: int = 1000) -> str:
    """Query PostgreSQL table and return data as JSON.
    
    Args:
        connection_string: PostgreSQL connection string
        table_name: Name of the table to query
        limit: Maximum number of rows to return
    
    Returns:
        JSON string with table data
    """
    try:
        engine = create_engine(connection_string)
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        return df.to_json(orient='records')
    
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


@tool
def explore_mongodb_database(connection_string: str, database_name: str) -> str:
    """Explore MongoDB database and get collection information.
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
    
    Returns:
        JSON string with database schema information
    """
    try:
        client = MongoClient(connection_string)
        db = client[database_name]
        
        result = {
            "collections": [],
            "total_collections": 0
        }
        
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            
            sample_doc = collection.find_one()
            fields = []
            if sample_doc:
                for key, value in sample_doc.items():
                    fields.append({
                        "name": key,
                        "type": type(value).__name__
                    })
            
            result["collections"].append({
                "name": collection_name,
                "fields": fields,
                "field_count": len(fields),
                "document_count": collection.count_documents({})
            })
        
        result["total_collections"] = len(result["collections"])
        client.close()
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


@tool
def query_mongodb_collection(connection_string: str, database_name: str, collection_name: str, limit: int = 1000) -> str:
    """Query MongoDB collection and return data as JSON.
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
        collection_name: Name of the collection to query
        limit: Maximum number of documents to return
    
    Returns:
        JSON string with collection data
    """
    try:
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        
        documents = list(collection.find().limit(limit))
        
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        client.close()
        
        return json.dumps(documents)
    
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})
