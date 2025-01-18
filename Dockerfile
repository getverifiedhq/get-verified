FROM node:latest

WORKDIR /usr/src/app

COPY . .

RUN npm install

RUN npm run build

RUN npm test

CMD [ "node", "dist/main.js" ]