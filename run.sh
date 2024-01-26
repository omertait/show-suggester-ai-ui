#!/bin/bash

# Navigate to the server directory and start the Flask server
echo "Starting Flask server..."

# Activate your Python virtual environment if you have one
python server/app.py &
# Save the Flask server's PID
FLASK_PID=$!

# Navigate to the client directory and start the React app
echo "Starting React client..."
cd ./client

npm start &
# Save the React server's PID
REACT_PID=$!

# Wait for the React process to finish
wait $REACT_PID

# When React process ends, kill the Flask server process
kill $FLASK_PID
