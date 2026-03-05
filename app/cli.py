import subprocess
import sys
import uvicorn

def dev():
    """Run the application in development mode with reload enabled."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

def start():
    """Run the application in production mode."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

def test():
    """Run the test suite."""
    subprocess.run(["pytest", "-v"] + sys.argv[1:])

def migrate():
    """Apply database migrations."""
    subprocess.run(["alembic", "upgrade", "head"] + sys.argv[1:])

def makemigrations():
    """Generate a new migration file."""
    args = sys.argv[1:]
    command = ["alembic", "revision", "--autogenerate"]
    
    # Check if a message was already provided in args
    if not any(arg in ["-m", "--message"] for arg in args):
        command += ["-m", "Add roles for users"]
    
    subprocess.run(command + args)
