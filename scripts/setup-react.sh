#!/bin/bash
# React Setup Script for AI Nurse Florence

echo "🏥 Setting up React frontend for AI Nurse Florence..."

# Navigate to React directory
cd /Users/patrickroebuck/projects/ai-nurse-florence/frontend-react

# Install dependencies
echo "📦 Installing React dependencies..."
npm install

# Install additional healthcare-specific packages
echo "🔧 Installing healthcare-specific packages..."
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest jsdom

# Copy Tailwind config from main frontend
echo "🎨 Setting up Tailwind CSS..."
cp ../frontend/tailwind.config.js ./tailwind.config.js

# Create PostCSS config
cat > postcss.config.js << EOF
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Start development server
echo "🚀 Starting React development server..."
echo "Frontend will be available at http://localhost:3000"
echo "Backend API proxy: http://localhost:3000/api -> http://localhost:8000/api"

npm run dev
