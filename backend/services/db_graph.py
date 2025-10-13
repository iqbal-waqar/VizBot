from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from backend.services.llm import get_llm
from backend.services.db_tools import (
    explore_postgresql_database,
    query_postgresql_table,
    explore_mongodb_database,
    query_mongodb_collection
)
from backend.services.tools import analyze_basic_stats, get_visualization_data
from backend.services.prompts import NARRATIVE_SUMMARY_PROMPT
import json


class DatabaseAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    db_type: str
    connection_string: str
    database_name: str
    database_info: dict
    analysis_results: dict
    narrative_summary: str
    table_data: dict  


def explore_database_node(state: DatabaseAgentState):
    db_type = state["db_type"]
    connection_string = state["connection_string"]
    database_name = state.get("database_name", "")
    
    if db_type == "postgresql":
        db_info = explore_postgresql_database.invoke({"connection_string": connection_string})
        db_info_dict = json.loads(db_info)
    else: 
        db_info = explore_mongodb_database.invoke({
            "connection_string": connection_string,
            "database_name": database_name
        })
        db_info_dict = json.loads(db_info)
    
    return {
        "database_info": db_info_dict,
        "messages": [AIMessage(content=f"Database exploration completed. Found {db_info_dict.get('total_tables', db_info_dict.get('total_collections', 0))} tables/collections.")]
    }


def analyze_tables_node(state: DatabaseAgentState):
    db_type = state["db_type"]
    connection_string = state["connection_string"]
    database_name = state.get("database_name", "")
    database_info = state["database_info"]
    
    table_analyses = []
    table_data = {}
    
    if db_type == "postgresql":
        tables = database_info.get("tables", [])[:3]  
        
        for table in tables:
            table_name = table["name"]
            
            data_json = query_postgresql_table.invoke({
                "connection_string": connection_string,
                "table_name": table_name,
                "limit": 1000
            })
            
            try:
                basic_stats = analyze_basic_stats.invoke({"df_json": data_json})
                table_analyses.append({
                    "table_name": table_name,
                    "stats": json.loads(basic_stats),
                    "type": "table"
                })
                table_data[table_name] = data_json
            except:
                pass
    
    else: 
        collections = database_info.get("collections", [])[:3] 
        
        for collection in collections:
            collection_name = collection["name"]
            
            data_json = query_mongodb_collection.invoke({
                "connection_string": connection_string,
                "database_name": database_name,
                "collection_name": collection_name,
                "limit": 1000
            })
            
            try:
                basic_stats = analyze_basic_stats.invoke({"df_json": data_json})
                table_analyses.append({
                    "collection_name": collection_name,
                    "stats": json.loads(basic_stats),
                    "type": "collection"
                })
                table_data[collection_name] = data_json
            except:
                pass
    
    return {
        "analysis_results": {"table_analyses": table_analyses},
        "table_data": table_data,
        "messages": [AIMessage(content=f"Analyzed {len(table_analyses)} tables/collections")]
    }


def database_visualization_node(state: DatabaseAgentState):
    table_data = state["table_data"]
    analysis_results = state["analysis_results"]
    
    all_visualizations = {}
    
    for table_name, data_json in table_data.items():
        viz_data = {
            "univariate": [],
            "bivariate": []
        }
        
        table_stats = None
        for analysis in analysis_results["table_analyses"]:
            if analysis.get("table_name") == table_name or analysis.get("collection_name") == table_name:
                table_stats = analysis["stats"]
                break
        
        if not table_stats:
            continue
            
        numerical_cols = table_stats.get("numerical_columns", [])
        categorical_cols = table_stats.get("categorical_columns", [])
        
        for col in numerical_cols[:3]:  
            try:
                hist_data = get_visualization_data.invoke({
                    "df_json": data_json,
                    "chart_type": "histogram",
                    "column": col
                })
                viz_data["univariate"].append({
                    "type": "histogram",
                    "column": col,
                    "table": table_name,
                    "data": json.loads(hist_data)
                })
            except:
                pass
        
        for col in categorical_cols[:3]:  
            try:
                if table_stats["categorical_stats"][col]["unique_values"] <= 15:
                    bar_data = get_visualization_data.invoke({
                        "df_json": data_json,
                        "chart_type": "bar",
                        "column": col
                    })
                    viz_data["univariate"].append({
                        "type": "bar",
                        "column": col,
                        "table": table_name,
                        "data": json.loads(bar_data)
                    })
                    
                    if table_stats["categorical_stats"][col]["unique_values"] <= 10:
                        pie_data = get_visualization_data.invoke({
                            "df_json": data_json,
                            "chart_type": "pie",
                            "column": col
                        })
                        viz_data["univariate"].append({
                            "type": "pie",
                            "column": col,
                            "table": table_name,
                            "data": json.loads(pie_data)
                        })
            except:
                pass
        
        if len(numerical_cols) >= 2:
            try:
                scatter_data = get_visualization_data.invoke({
                    "df_json": data_json,
                    "chart_type": "scatter",
                    "column": numerical_cols[0],
                    "second_column": numerical_cols[1]
                })
                viz_data["bivariate"].append({
                    "type": "scatter",
                    "table": table_name,
                    "data": json.loads(scatter_data)
                })
            except:
                pass
        
        all_visualizations[table_name] = viz_data
    
    analysis_results["visualizations"] = all_visualizations
    
    return {
        "analysis_results": analysis_results,
        "messages": [AIMessage(content="Database visualization data prepared")]
    }


def database_narrative_node(state: DatabaseAgentState):
    llm = get_llm()
    database_info = state["database_info"]
    analysis_results = state["analysis_results"]
    db_type = state["db_type"]
    
    analysis_for_llm = {
        "table_analyses": analysis_results.get("table_analyses", [])
    }
    
    prompt = f"""{NARRATIVE_SUMMARY_PROMPT}

Database Type: {db_type.upper()}

Database Structure:
{json.dumps(database_info, indent=2)}

Analysis Results:
{json.dumps(analysis_for_llm, indent=2)}

Generate a comprehensive narrative summary of the database analysis, including:
- Database overview and structure
- Key insights from analyzed tables/collections
- Data quality observations
- Notable patterns or issues discovered
"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "narrative_summary": response.content,
        "messages": [AIMessage(content="Database narrative summary generated")]
    }


def create_database_analysis_graph():
    workflow = StateGraph(DatabaseAgentState)
    
    workflow.add_node("explore", explore_database_node)
    workflow.add_node("analyze", analyze_tables_node)
    workflow.add_node("visualizations", database_visualization_node)
    workflow.add_node("narrative", database_narrative_node)
    
    workflow.set_entry_point("explore")
    workflow.add_edge("explore", "analyze")
    workflow.add_edge("analyze", "visualizations")
    workflow.add_edge("visualizations", "narrative")
    workflow.add_edge("narrative", END)
    
    app = workflow.compile()
    return app
