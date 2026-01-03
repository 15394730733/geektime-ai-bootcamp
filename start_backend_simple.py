#!/usr/bin/env python3
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'w2', 'sth-db-query', 'backend')
sys.path.insert(0, backend_path)

try:
    # Import the FastAPI app
    from app.main import app
    import uvicorn

    print("Starting Database Query Tool backend...")
    print(f"Backend path: {backend_path}")

    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

except Exception as e:
    print(f"Error starting backend: {e}")
    import traceback
    traceback.print_exc()
