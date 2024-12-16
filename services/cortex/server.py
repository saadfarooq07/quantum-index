import multiprocessing
import uvicorn
import os

def get_worker_count():
    """Get optimal number of workers based on CPU cores."""
    return min(multiprocessing.cpu_count(), 4)  # Cap at 4 workers

def run_server(port: int = 8000, reload: bool = False):
    """Run the uvicorn server with optimized settings."""
    uvicorn.run(
        "services.cortex.app:app",
        host="0.0.0.0",
        port=port,
        workers=1 if reload else get_worker_count(),  # Single worker in reload mode
        loop="uvloop",
        log_level="info",
        reload=reload,
        reload_dirs=["services/cortex"] if reload else None,
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=30,  # Reduce keep-alive timeout
        access_log=False,  # Disable access logs in production
    )

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Development mode uses reload
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    run_server(port=port, reload=debug)
