import time
import uuid
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

ALLOWED_ORIGIN = "https://example.com"

@app.middleware("http")
async def dynamic_cors_and_headers(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    # Get the origin header sent by the client browser/grader
    incoming_origin = request.headers.get("origin")

    # 1. Handle Preflight OPTIONS requests
    if request.method == "OPTIONS":
        # Create a blank 200 OK response for the preflight check
        response = Response(status_code=200)
        
        # ONLY echo back the header if it matches your specific assigned origin
        if incoming_origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Request-ID, X-Process-Time"
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Always inject the required assignment tracking metrics
        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response

    # 2. Handle normal requests (GET /stats, etc.)
    response = await call_next(request)
    
    # Attach CORS header only if it matches your assigned origin
    if incoming_origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
    # Inject required assignment tracking metrics
    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Metrics API is running"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

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
