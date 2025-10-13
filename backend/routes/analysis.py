from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.interactors.analyzer import DataAnalyzer
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["analysis"])

analyzer = DataAnalyzer()


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_data(file: UploadFile = File(...)):
    try:
        result = await analyzer.analyze_uploaded_file(file)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VizBot Analytics API"}
