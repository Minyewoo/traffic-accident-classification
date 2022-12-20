FROM node:19-alpine
WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm ci --only=production
COPY . /app
EXPOSE 8080
CMD [ "node", "index.js" ]