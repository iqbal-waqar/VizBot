from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from backend.services.llm import get_llm
from backend.services.tools import (
    analyze_basic_stats,
    detect_outliers,
    analyze_correlations,
    get_visualization_data
)
from backend.services.prompts import NARRATIVE_SUMMARY_PROMPT
import json


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    df_json: str
    analysis_results: dict
    narrative_summary: str


def analysis_node(state: AgentState):
    df_json = state["df_json"]
    
    basic_stats = analyze_basic_stats.invoke({"df_json": df_json})
    outliers = detect_outliers.invoke({"df_json": df_json})
    correlations = analyze_correlations.invoke({"df_json": df_json})
    
    analysis_results = {
        "basic_stats": json.loads(basic_stats),
        "outliers": json.loads(outliers),
        "correlations": json.loads(correlations)
    }
    
    return {
        "analysis_results": analysis_results,
        "messages": [AIMessage(content="Analysis completed successfully")]
    }


def narrative_generation_node(state: AgentState):
    llm = get_llm()
    analysis_results = state["analysis_results"]
    
    prompt = f"""{NARRATIVE_SUMMARY_PROMPT}

Analysis Results:
{json.dumps(analysis_results, indent=2)}

Generate a comprehensive narrative summary of the dataset analysis."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "narrative_summary": response.content,
        "messages": [AIMessage(content="Narrative summary generated")]
    }


def visualization_prep_node(state: AgentState):
    df_json = state["df_json"]
    analysis_results = state["analysis_results"]
    
    viz_data = {
        "univariate": [],
        "bivariate": []
    }
    
    numerical_cols = analysis_results["basic_stats"].get("numerical_columns", [])
    categorical_cols = analysis_results["basic_stats"].get("categorical_columns", [])
    
    for col in numerical_cols[:5]:
        hist_data = get_visualization_data.invoke({
            "df_json": df_json,
            "chart_type": "histogram",
            "column": col
        })
        chart_data = json.loads(hist_data)
        viz_data["univariate"].append({
            "type": "histogram",
            "column": col,
            **chart_data  
        })
    
    for col in categorical_cols[:5]:
        if analysis_results["basic_stats"]["categorical_stats"][col]["unique_values"] <= 15:
            bar_data = get_visualization_data.invoke({
                "df_json": df_json,
                "chart_type": "bar",
                "column": col
            })
            chart_data = json.loads(bar_data)
            viz_data["univariate"].append({
                "type": "bar",
                "column": col,
                **chart_data  
            })
            
            if analysis_results["basic_stats"]["categorical_stats"][col]["unique_values"] <= 10:
                pie_data = get_visualization_data.invoke({
                    "df_json": df_json,
                    "chart_type": "pie",
                    "column": col
                })
                chart_data = json.loads(pie_data)
                viz_data["univariate"].append({
                    "type": "pie",
                    "column": col,
                    **chart_data  
                })
    
    if len(numerical_cols) >= 2:
        for i in range(min(3, len(numerical_cols)-1)):
            scatter_data = get_visualization_data.invoke({
                "df_json": df_json,
                "chart_type": "scatter",
                "column": numerical_cols[i],
                "second_column": numerical_cols[i+1]
            })
            chart_data = json.loads(scatter_data)
            viz_data["bivariate"].append({
                "type": "scatter",
                **chart_data 
            })
        
        heatmap_data = get_visualization_data.invoke({
            "df_json": df_json,
            "chart_type": "correlation_heatmap",
            "column": "correlation" 
        })
        chart_data = json.loads(heatmap_data)
        viz_data["bivariate"].append({
            "type": "correlation_heatmap",
            **chart_data  
        })
    
    analysis_results["visualizations"] = viz_data
    
    return {
        "analysis_results": analysis_results,
        "messages": [AIMessage(content="Visualization data prepared")]
    }


def create_analysis_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("narrative", narrative_generation_node)
    workflow.add_node("visualizations", visualization_prep_node)
    
    workflow.set_entry_point("analysis")
    workflow.add_edge("analysis", "narrative")
    workflow.add_edge("narrative", "visualizations")
    workflow.add_edge("visualizations", END)
    
    app = workflow.compile()
    return app
