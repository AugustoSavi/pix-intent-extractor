import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add the root directory to sys.path to import pix_classifier
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pix_classifier.classifier import extrair_pix

app = FastAPI(title="Pix Classifier API")
app.mount("/public", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public")), name="public")

class PixRequest(BaseModel):
    text: str

@app.post("/classify")
async def classify_pix(request: PixRequest):
    try:
        result = extrair_pix(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "resultados.json")
    if not os.path.exists(results_path):
        return []
    try:
        import json
        with open(results_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
