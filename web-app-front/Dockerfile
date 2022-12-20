FROM node:19-alpine as builder
WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm ci --only=production
COPY . /app
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL $REACT_APP_API_URL
ENV REACT_APP_KAVO kek
RUN npm run build

FROM nginx:1.23.1-alpine as production
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80