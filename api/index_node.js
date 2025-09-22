const { spawn } = require('child_process');
const path = require('path');

module.exports = async (req, res) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'python_handler.py')
    ], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let error = '';

    // Send request data to Python
    pythonProcess.stdin.write(JSON.stringify({
      url: req.url,
      method: req.method,
      headers: req.headers,
      query: req.query,
      body: req.body
    }));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        res.status(500).json({ error: 'Python process failed', details: error });
        return resolve();
      }

      try {
        const result = JSON.parse(output);
        res.status(result.statusCode || 200);
        
        if (result.headers) {
          Object.entries(result.headers).forEach(([key, value]) => {
            res.setHeader(key, value);
          });
        }
        
        res.send(result.body || result);
        resolve();
      } catch (e) {
        res.status(500).json({ error: 'Failed to parse Python response', details: e.message });
        resolve();
      }
    });
  });
};
