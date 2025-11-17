from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from flan_t5_parser import FlanT5Parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NLP Service API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = None


class ParseRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    use_rasa: bool = False


class ParseResponse(BaseModel):
    intent: str
    entities: Dict[str, Any]
    edit_command: Dict[str, Any]
    confidence: float
    human_preview: str
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    global parser
    logger.info("Initializing Flan-T5 parser...")
    parser = FlanT5Parser()
    logger.info("NLP service ready")


@app.post("/parse", response_model=ParseResponse)
async def parse_message(request: ParseRequest):
    try:
        if not parser:
            raise HTTPException(status_code=503, detail="Parser not initialized")

        result = parser.parse(request.message, request.context)

        return ParseResponse(
            intent=result["intent"],
            entities=result["entities"],
            edit_command=result["edit_command"],
            confidence=result["confidence"],
            human_preview=result["human_preview"],
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Parse error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "parser_loaded": parser is not None
    }


@app.get("/")
async def root():
    return {
        "service": "NLP Service",
        "version": "1.0.0",
        "endpoints": {
            "/parse": "POST - Parse user messages",
            "/health": "GET - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
