# production/frontend/Dockerfile

# Stage 1: Build the React Application
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies first (for caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY . ./

# Build the production bundle using Vite/React
RUN npm run build

# Stage 2: Serve via NGINX
FROM nginx:alpine

# Copy the build artifacts from the builder stage
# (Vite defaults to creating a 'dist' folder)
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
