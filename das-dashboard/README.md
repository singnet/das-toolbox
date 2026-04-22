### DAS UI for Configuration/Setup

This is a simple and intuitive web interface, created to make das/das-cli's setup easier to do and to visualize.

### Running the interface locally:

1. If you are in the DAS' project main folder, change to './das-dashboard'
2. Run 'npm install'
3. Run 'npm run dev'

### Running locally via docker:
1. On your terminal, run 'docker build -t das-dashboard .'
2. Then run 'docker run -d --network host --name das-dashboard das-dashboard:latest' and you'll have a node server hosting the interface locally.

That's all, you should be able to run the web app perfectly and use its full features.
