### DAS UI for Configuration/Setup

This is a simple and intuitive web interface, created to make das/das-cli's setup easier to do and to visualize.

### Requirements:

- Node version (From version 22.0 and up)
(You can verify your node version by typing 'node -v')

- If node isn't version 22 or higher. We recommend that you run this command:

> (Make sure you have the NVM tool, in case you don't have it, read [this](https://github.com/nvm-sh/nvm#install--update-script))
> 'nvm install node --lts'
  
### Running the interface locally:
1. If you are in the root folder of the DAS project, change directory to './das-dashboard'
2. Run 'npm install'
3. Run 'npm run dev'

### Running locally via docker:
1. If you are in the root folder of the DAS project, change directory to './das-dashboard'
2. On your terminal, run 'docker build -t das-dashboard .'
3. Then run 'docker run -d --network host --name das-dashboard das-dashboard:latest' and you'll have a node server hosting the interface locally.

That's all, you should be able to run the web app perfectly and use its full features.
