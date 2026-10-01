"""FastAPI app. Run from the project root: uvicorn app.backend.main:app --reload"""
import importlib

from fastapi import Body, FastAPI, File, Form, Request, UploadFile
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import config, llm, pipeline
from .errors import AppError

app = FastAPI(title="Adhikar Saathi", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(AppError)
async def _app_error(_: Request, exc: AppError):
    return JSONResponse(exc.payload(), status_code=exc.status)


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(AppError("bad_request").payload(), status_code=400)


@app.exception_handler(StarletteHTTPException)
async def _http_error(request: Request, exc: StarletteHTTPException):
    if not request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    return JSONResponse(AppError("bad_request", str(exc.detail)).payload(), status_code=exc.status_code)


@app.get("/api/health")
def health():
    return {"ok": True, "providers": llm.available_providers(), "cards": pipeline.card_count(),
            "mock": config.mock_mode()}


@app.post("/api/ask")
def ask(
    session_id: str | None = Form(None),
    text: str | None = Form(None),
    audio: UploadFile | None = File(None),
    want_audio: str = Form("true"),
    provider: str | None = Form(None),
    retrieval: str | None = Form(None),
    language: str | None = Form(None),
):
    audio_tuple = None
    if audio is not None and audio.filename is not None:
        data = audio.file.read(config.MAX_AUDIO_BYTES + 1)
        if len(data) > config.MAX_AUDIO_BYTES:
            raise AppError("bad_request", "Audio file is larger than 5 MB.")
        if data:
            audio_tuple = (data, audio.filename or "audio.webm", audio.content_type or "audio/webm")
    return pipeline.ask(
        session_id=session_id or None,
        text=text,
        audio=audio_tuple,
        want_audio=want_audio.strip().lower() not in ("false", "0", "no", "off"),
        provider=provider or None,
        retrieval=retrieval or None,
        language=(language or "").strip() or None,
    )


def _optional_module(name: str, fn: str):
    """Import a module owned by another agent; None if it does not exist yet."""
    full = f"app.backend.{name}"
    try:
        return getattr(importlib.import_module(full), fn)
    except ModuleNotFoundError as e:
        if e.name == full:
            return None
        raise


def _not_implemented(what: str):
    return JSONResponse(
        {"error": {"code": "bad_request", "message_hi": "यह सुविधा अभी तैयार नहीं है।",
                   "message_en": f"{what} is not available yet (module not implemented)."}},
        status_code=501)


@app.post("/api/schemes")
def schemes(payload: dict = Body(default_factory=dict)):
    match = _optional_module("schemes", "match")
    if match is None:
        return _not_implemented("Scheme matching")
    return match(payload)


@app.post("/api/complaint-draft")
def complaint_draft(payload: dict = Body(default_factory=dict)):
    draft = _optional_module("complaint", "draft")
    if draft is None:
        return _not_implemented("Complaint drafting")
    return draft(payload)


class _FreshStaticFiles(StaticFiles):
    # Browsers otherwise reuse stale app.js/style.css next to a newer index.html and the page breaks.
    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


# Registered last so it never shadows /api. The frontend is only mounted if it exists at startup.
if (config.FRONTEND_DIR / "index.html").exists():
    app.mount("/", _FreshStaticFiles(directory=str(config.FRONTEND_DIR), html=True), name="frontend")
