FROM node:22-alpine
WORKDIR /app
COPY services/api-typescript/package*.json ./
RUN npm ci
COPY services/api-typescript/tsconfig.json ./
COPY services/api-typescript/src ./src
RUN npm run build
CMD ["node", "dist/index.js"]
