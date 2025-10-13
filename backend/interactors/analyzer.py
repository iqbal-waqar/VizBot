import pandas as pd
from io import BytesIO
from backend.services.graph import create_analysis_graph
from typing import Dict, Any


class DataAnalyzer:
    def __init__(self):
        self.graph = create_analysis_graph()
    
    async def analyze_csv(self, file_content: bytes) -> Dict[str, Any]:
        """
        Analyze CSV file and return comprehensive analysis results.
        
        Args:
            file_content: Raw bytes of the CSV file
            
        Returns:
            Dictionary containing narrative summary and analysis results
        """
        try:
            df = pd.read_csv(BytesIO(file_content))
            
            if df.empty:
                raise ValueError("CSV file is empty")
            
            df_json = df.to_json(orient='records')
            
            initial_state = {
                "messages": [],
                "df_json": df_json,
                "analysis_results": {},
                "narrative_summary": ""
            }
            
            final_state = self.graph.invoke(initial_state)
            
            response = {
                "narrative_summary": final_state["narrative_summary"],
                "analysis_results": final_state["analysis_results"],
                "status": "success",
                "message": "Analysis completed successfully"
            }
            
            return response
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or invalid")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error during analysis: {str(e)}")
    
    async def analyze_uploaded_file(self, file) -> Dict[str, Any]:
        """
        Analyze uploaded file with validation.
        
        Args:
            file: UploadFile object from FastAPI
            
        Returns:
            Dictionary containing analysis results
        """

        if not file.filename or not file.filename.endswith('.csv'):
            raise ValueError("Only CSV files are supported")
        

        content = await file.read()
        

        if not content:
            raise ValueError("File is empty")
        
 
        return await self.analyze_csv(content)
