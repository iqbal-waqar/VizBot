import pandas as pd
import numpy as np
from langchain_core.tools import tool
from typing import Dict, Any
import json
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils

@tool
def analyze_basic_stats(df_json: str) -> str:
    """Analyze basic statistics and data quality of the dataset.
    
    Args:
        df_json: JSON string representation of the dataframe
    
    Returns:
        JSON string with basic statistics and data quality info
    """
    df = pd.read_json(StringIO(df_json))
    
    result = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "missing_percentage": {col: float(round(df[col].isna().sum() / len(df) * 100, 2)) for col in df.columns},
        "duplicates": int(df.duplicated().sum()),
        "memory_usage": float(round(df.memory_usage(deep=True).sum() / 1024**2, 2)),
        "numerical_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=['datetime64']).columns.tolist()
    }
    
    numerical_stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        clean_series = df[col].dropna()
        if len(clean_series) > 0:
            finite_series = clean_series[np.isfinite(clean_series)]
            if len(finite_series) > 0:
                numerical_stats[col] = {
                    "mean": float(finite_series.mean()),
                    "median": float(finite_series.median()),
                    "std": float(finite_series.std()) if len(finite_series) > 1 else 0.0,
                    "min": float(finite_series.min()),
                    "max": float(finite_series.max()),
                    "q25": float(finite_series.quantile(0.25)),
                    "q75": float(finite_series.quantile(0.75)),
                    "count": int(len(finite_series)),
                    "null_count": int(len(df[col]) - len(clean_series)),
                    "infinite_count": int(len(clean_series) - len(finite_series))
                }
            else:
                numerical_stats[col] = {
                    "mean": None,
                    "median": None,
                    "std": None,
                    "min": None,
                    "max": None,
                    "q25": None,
                    "q75": None,
                    "count": 0,
                    "null_count": int(len(df[col]) - len(clean_series)),
                    "infinite_count": int(len(clean_series))
                }
        else:
            numerical_stats[col] = {
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "q25": None,
                "q75": None,
                "count": 0,
                "null_count": int(len(df[col])),
                "infinite_count": 0
            }
    
    categorical_stats = {}
    for col in df.select_dtypes(include=['object', 'category']).columns:
        clean_series = df[col].dropna()
        if len(clean_series) > 0:
            value_counts = clean_series.value_counts().head(10)
            mode_values = clean_series.mode()
            categorical_stats[col] = {
                "unique_values": int(clean_series.nunique()),
                "mode": str(mode_values.iloc[0]) if len(mode_values) > 0 else None,
                "top_values": {str(k): int(v) for k, v in value_counts.items()},
                "total_count": int(len(clean_series)),
                "null_count": int(len(df[col]) - len(clean_series))
            }
        else:
            categorical_stats[col] = {
                "unique_values": 0,
                "mode": None,
                "top_values": {},
                "total_count": 0,
                "null_count": int(len(df[col]))
            }
    
    result["numerical_stats"] = numerical_stats
    result["categorical_stats"] = categorical_stats
    
    return json.dumps(result)


@tool
def detect_outliers(df_json: str) -> str:
    """Detect outliers in numerical columns using IQR method.
    
    Args:
        df_json: JSON string representation of the dataframe
    
    Returns:
        JSON string with outlier information
    """
    df = pd.read_json(StringIO(df_json))
    outliers = {}
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        if df[col].notna().sum() > 0:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                outliers[col] = {
                    "count": int(outlier_count),
                    "percentage": float(round(outlier_count / len(df) * 100, 2)),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "outlier_values": df[df[col] < lower_bound][col].tolist()[:5] + 
                                     df[df[col] > upper_bound][col].tolist()[:5]
                }
    
    return json.dumps(outliers)


@tool
def analyze_correlations(df_json: str) -> str:
    """Analyze correlations between numerical variables.
    
    Args:
        df_json: JSON string representation of the dataframe
    
    Returns:
        JSON string with correlation matrix and insights
    """
    df = pd.read_json(StringIO(df_json))
    numerical_df = df.select_dtypes(include=[np.number])
    
    if len(numerical_df.columns) < 2:
        return json.dumps({"error": "Not enough numerical columns for correlation analysis"})
    
    clean_numerical_df = numerical_df.copy()
    for col in numerical_df.columns:
        clean_series = numerical_df[col].dropna()
        finite_series = clean_series[np.isfinite(clean_series)]
        if len(finite_series) == 0:
            clean_numerical_df = clean_numerical_df.drop(columns=[col])
    
    if len(clean_numerical_df.columns) < 2:
        return json.dumps({"error": "Not enough valid numerical columns for correlation analysis"})
    
    corr_matrix = clean_numerical_df.corr(method='pearson')
    
    result = {
        "correlation_matrix": {
            col: {c: float(corr_matrix.loc[col, c]) if not pd.isna(corr_matrix.loc[col, c]) else None 
                  for c in corr_matrix.columns}
            for col in corr_matrix.columns
        },
        "strong_correlations": []
    }
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            
            if abs(corr_value) > 0.5 and not pd.isna(corr_value):
                result["strong_correlations"].append({
                    "variable1": col1,
                    "variable2": col2,
                    "correlation": float(corr_value),
                    "strength": "strong positive" if corr_value > 0.7 else "moderate positive" if corr_value > 0.5 else "strong negative" if corr_value < -0.7 else "moderate negative"
                })
    
    return json.dumps(result)


@tool
def get_visualization_data(df_json: str, chart_type: str, column: str, second_column: str = None) -> str:
    """Generate complete Plotly charts for specific visualization types.
    
    Args:
        df_json: JSON string representation of the dataframe
        chart_type: Type of chart (histogram, bar, pie, scatter, etc.)
        column: Primary column for visualization
        second_column: Secondary column for bivariate charts (optional)
    
    Returns:
        JSON string with complete Plotly chart object or error message
    """
    try:
        df = pd.read_json(StringIO(df_json))
        
        if chart_type != "correlation_heatmap" and column not in df.columns:
            return json.dumps({"error": f"Column '{column}' not found in data"})
        
        result = {"chart_type": chart_type, "column": column}
        
        if chart_type == "histogram":
            if column in df.select_dtypes(include=[np.number]).columns:
                clean_values = df[column].dropna()
                if len(clean_values) == 0:
                    return json.dumps({"error": f"No valid data for histogram of column '{column}'"})
                
                finite_values = clean_values[np.isfinite(clean_values)]
                
                if len(finite_values) == 0:
                    return json.dumps({"error": f"No finite numeric values for histogram of column '{column}'"})
                
                fig = px.histogram(
                    x=finite_values,
                    nbins=min(30, max(5, int(np.sqrt(len(finite_values))))),
                    labels={"x": column, "y": "Frequency"},
                    title=f"Distribution of {column}"
                )
                
                result["plotly_chart"] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
                
            else:
                return json.dumps({"error": f"Column '{column}' is not numeric for histogram"})
        
        elif chart_type == "bar" or chart_type == "countplot":
            clean_series = df[column].dropna()
            if len(clean_series) == 0:
                return json.dumps({"error": f"No valid data for bar chart of column '{column}'"})
            
            value_counts = clean_series.value_counts().head(15)
            if len(value_counts) == 0:
                return json.dumps({"error": f"No data to plot for column '{column}'"})
            
            fig = px.bar(
                x=[str(label) for label in value_counts.index],
                y=value_counts.values,
                labels={"x": column, "y": "Count"},
                title=f"Count Plot of {column}"
            )
            
            result["plotly_chart"] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
        
        elif chart_type == "pie":
            clean_series = df[column].dropna()
            if len(clean_series) == 0:
                return json.dumps({"error": f"No valid data for pie chart of column '{column}'"})
            
            value_counts = clean_series.value_counts().head(10)
            if len(value_counts) == 0:
                return json.dumps({"error": f"No data to plot for column '{column}'"})
            
            fig = px.pie(
                names=[str(label) for label in value_counts.index],
                values=value_counts.values,
                title=f"Distribution of {column}"
            )
            
            result["plotly_chart"] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
        
        elif chart_type == "scatter" and second_column:
            if second_column not in df.columns:
                return json.dumps({"error": f"Second column '{second_column}' not found in data"})
            
            if column not in df.select_dtypes(include=[np.number]).columns:
                return json.dumps({"error": f"Column '{column}' is not numeric for scatter plot"})
            
            if second_column not in df.select_dtypes(include=[np.number]).columns:
                return json.dumps({"error": f"Column '{second_column}' is not numeric for scatter plot"})
            
            clean_df = df[[column, second_column]].dropna()
            if len(clean_df) == 0:
                return json.dumps({"error": f"No valid data pairs for scatter plot of '{column}' vs '{second_column}'"})
            
            clean_df = clean_df[np.isfinite(clean_df[column]) & np.isfinite(clean_df[second_column])]
            if len(clean_df) == 0:
                return json.dumps({"error": f"No finite data pairs for scatter plot of '{column}' vs '{second_column}'"})
            
            fig = px.scatter(
                x=clean_df[column],
                y=clean_df[second_column],
                labels={"x": column, "y": second_column},
                title=f"{column} vs {second_column}"
            )
            
            result["plotly_chart"] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
            result["second_column"] = second_column
        
        elif chart_type == "correlation_heatmap":
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                return json.dumps({"error": "No numerical columns available for correlation heatmap"})
            
            clean_numeric_df = numeric_df.dropna(axis=1, how='all')
            for col in clean_numeric_df.columns:
                clean_numeric_df = clean_numeric_df[clean_numeric_df[col].replace([np.inf, -np.inf], np.nan).notna()]
            
            if clean_numeric_df.empty or len(clean_numeric_df.columns) < 2:
                return json.dumps({"error": "Insufficient valid numerical data for correlation heatmap"})
            
            corr_matrix = clean_numeric_df.corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="Correlation Matrix"
            )
            
            result["plotly_chart"] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
        
        else:
            return json.dumps({"error": f"Unsupported chart type: {chart_type}"})
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Error generating chart: {str(e)}"})
