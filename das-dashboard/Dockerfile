FROM node:25-slim

COPY . /das-dashboard
WORKDIR /das-dashboard

RUN npm install

ENTRYPOINT ["npm", "run", "dev"]