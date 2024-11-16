FLASK_APP=app.py

# Since we are only using flask as a backend and is not serving the web page, the browser
# based debugger is irrelevant. Errors should still be visible on command line. 
# FLASK_DEBUG=False

# Actually, I turned it on for hot reloading
FLASK_DEBUG=True

FLASK_RUN_PORT=5000
FLASK_RUN_HOST=127.0.0.1
