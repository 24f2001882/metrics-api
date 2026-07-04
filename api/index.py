import time
import uuid
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. Strict CORS Configuration
ALLOWED_ORIGIN = "https://example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],  # Only allow your specific assigned origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Custom Middleware for Headers (Request ID & Process Time)
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    response = await call_next(request)
    
    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# 🌟 ADDED: Fallback root route so visiting the base URL directly doesn't throw a 404
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Metrics API is running"}

# 🌟 ADDED: The missing ping route required by your grader
@app.get("/ping")
async def ping():
    return {"status": "ok"}

# 3. The Metrics Statistics Endpoint
@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        num_list = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid integers provided"})

    if not num_list:
        return JSONResponse(status_code=400, content={"error": "Empty list provided"})

    count_val = len(num_list)
    sum_val = sum(num_list)
    min_val = min(num_list)
    max_val = max(num_list)
    mean_val = sum_val / count_val

    return {
        "email": "24f2001882@ds.study.iitm.ac.in", 
        "count": count_val,
        "sum": sum_val,
        "min": min_val,
        "max": max_val,
        "mean": round(mean_val, 4)
    }
