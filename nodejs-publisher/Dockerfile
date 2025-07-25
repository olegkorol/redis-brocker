FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port (not needed for this app but good practice)
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
