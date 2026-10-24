import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional

from app.extractor import extract_media_info, COOKIES_PATH
from app.downloader import download_media, cleanup_file

app = FastAPI(title="Universal Media Downloader", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InspectRequest(BaseModel):
    url: str

class CookieTextRequest(BaseModel):
    cookies: str

@app.post("/api/inspect")
async def inspect_url(req: InspectRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="Please provide a valid URL.")
    try:
        data = await run_in_threadpool(extract_media_info, req.url.strip())
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download")
async def handle_download(
    background_tasks: BackgroundTasks,
    url: str = Query(...),
    option_type: str = Query(..., alias="type"),
    format_spec: Optional[str] = Query(None),
    direct_url: Optional[str] = Query(None),
    ext: str = Query("mp4"),
    title: str = Query("media")
):
    try:
        file_path, filename = await run_in_threadpool(
            download_media,
            url=url,
            option_type=option_type,
            format_spec=format_spec,
            direct_url=direct_url,
            ext=ext,
            title=title
        )

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Downloaded file could not be found.")

        background_tasks.add_task(cleanup_file, file_path)

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

TUNNEL_FILE = os.path.join(os.path.dirname(__file__), "tunnel_url.txt")

@app.get("/api/tunnel/info")
async def get_tunnel_info():
    if os.path.exists(TUNNEL_FILE):
        try:
            with open(TUNNEL_FILE, "r", encoding="utf-8") as f:
                url = f.read().strip()
                if url.startswith("http"):
                    return {"tunnel_active": True, "public_url": url}
        except Exception:
            pass
    return {"tunnel_active": False, "public_url": None}

# Cookie Management Endpoints for bypassing YouTube bot checks
@app.get("/api/cookies/status")
async def get_cookies_status():
    has_cookies = os.path.exists(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 0
    return {"active": has_cookies, "path": COOKIES_PATH if has_cookies else None}

@app.post("/api/cookies/save")
async def save_cookies(req: CookieTextRequest):
    content = req.cookies.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Cookies content cannot be empty.")
    try:
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "message": "cookies.txt saved successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save cookies: {str(e)}")

@app.delete("/api/cookies/clear")
async def clear_cookies():
    try:
        if os.path.exists(COOKIES_PATH):
            os.remove(COOKIES_PATH)
        return {"success": True, "message": "Cookies cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
