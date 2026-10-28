# ============================================
# main.py - FastAPI Application Entry Point
# ============================================
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.routes import router
from app.core.config import settings

# ── Logging Setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ── Lifespan (replaces deprecated on_event) ────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    logger.info("📖 API Docs : http://localhost:8000/docs")
    logger.info("🌐 Frontend : http://localhost:8000/")
    yield
    # Shutdown
    logger.info("🛑 Server shutting down...")


# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    description="""
## 📄 Indian Journal Citation Parser API

An open API parser for extracting complete citation metadata from
**non-standard Indian Journal PDFs** and Conference Proceedings.

### Features
- 🔍 **PDF Upload** → Auto-extract title, authors, year, DOI, journal, etc.
- 🌐 **CrossRef API** → Free DOI-based metadata lookup (95%+ accuracy)
- 🤖 **OpenAI GPT** → AI-powered extraction for non-standard formats
- 📝 **BibTeX Export** → Ready-to-use .bib file entries
- 📋 **Citation Text Parsing** → Parse APA / MLA / IEEE formatted references

### Supported Formats
- **Referencing Styles**: APA, MLA, IEEE
- **Output**: BibTeX, JSON
- **Sources**: CrossRef, OpenAI GPT-4o-mini, Regex parsing

### Quick Start
1. Try `/parse/pdf` — upload any Indian journal PDF
2. Try `/parse/doi` — enter DOI like `10.1145/3474123.3474456`
3. Try `/parse/text` — paste APA/IEEE citation
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS Middleware ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routes ─────────────────────────────────────────────
app.include_router(router, prefix="/api/v1", tags=["Citation Parser"])

# ── Serve Frontend ─────────────────────────────────────────────
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
