### DAS UI - Mini Back-end
This is a small proxy server with the purpose of executing low-level tasks for the UI, such as executing shell, das-cli and saving files.

### Running the server separate from the UI.

1. If you are in the dashboard's directory, change dir to 'backend/'
2. Build the server's image by running: 'docker build -t ui_backend .'
3. Run '
  docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/das-cli:/usr/bin/das-cli:ro \
  -v /opt/web-das:/opt/web-das \
  --network=host \
  ui_backend:latest \
  uvicorn main:dashboard_app --host 0.0.0.0 --port 8000
'