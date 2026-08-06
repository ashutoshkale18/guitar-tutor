from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

# Rate limiting settings: 100 requests per 60 seconds
RATE_LIMIT = 100
TIME_WINDOW = 60

# In-memory store: { ip: [timestamp1, timestamp2, ...] }
request_counts = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # We only want to rate limit actual API endpoints, not static files or websockets
        if request.url.path.startswith("/api/"):
            # Clean up old requests
            if client_ip in request_counts:
                request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < TIME_WINDOW]
            else:
                request_counts[client_ip] = []
                
            # Check limit
            if len(request_counts[client_ip]) >= RATE_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."}
                )
                
            request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
