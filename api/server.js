const { spawn } = require('child_process');
const http = require('http');
const httpProxy = require('http-proxy-middleware');

let pythonProcess = null;
let pythonReady = false;

// Start Python FastAPI server
function startPythonServer() {
  console.log('Starting Python FastAPI server...');
  
  pythonProcess = spawn('python3', ['-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8001'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: __dirname + '/..'
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log('Python stdout:', data.toString());
    if (data.toString().includes('Uvicorn running')) {
      pythonReady = true;
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Python stderr:', data.toString());
  });

  pythonProcess.on('close', (code) => {
    console.log('Python process exited with code:', code);
    pythonReady = false;
  });
}

// Create proxy to Python server
const proxy = httpProxy.createProxyMiddleware({
  target: 'http://localhost:8001',
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      error: 'Python server not available', 
      details: err.message,
      pythonReady: pythonReady
    }));
  }
});

// Vercel serverless function
module.exports = async (req, res) => {
  // Start Python server if not running
  if (!pythonProcess) {
    startPythonServer();
    
    // Wait a bit for Python server to start
    await new Promise(resolve => setTimeout(resolve, 3000));
  }

  if (!pythonReady) {
    res.status(503).json({ 
      error: 'Python server starting up', 
      message: 'Please try again in a few seconds' 
    });
    return;
  }

  // Proxy request to Python server
  proxy(req, res);
};
