const express = require('express');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
const port = 3000;

// Middleware
const logData = (req, res, next) => {
  console.log(`HTTP Request : ${req.method} ${req.headers.host}${req.url}`);
  next();
};

app.use(logData);
app.use(express.json());

// Serve static assets and index.html
const publicDir = path.join(__dirname, 'public');
app.use(express.static(publicDir));

app.get('/', (req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});

// Proxy to Python APIs and combine /scan + /predict
const PY_BASE_URL = 'http://127.0.0.1:5000';

app.get('/api/scan-and-predict', async (req, res) => {
  try {
    // 1) Call Flask /scan
    const scanResp = await fetch(`${PY_BASE_URL}/scan`);
    if (!scanResp.ok) {
      return res
        .status(502)
        .json({ error: 'Failed to scan networks from Python backend' });
    }
    const scanData = await scanResp.json();
    console.log('Flask /scan response:', JSON.stringify(scanData, null, 2));

    // 2) Feed scan result into Flask /predict
    const predictResp = await fetch(`${PY_BASE_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scanData),
    });

    if (!predictResp.ok) {
      return res
        .status(502)
        .json({ error: 'Failed to predict networks from Python backend' });
    }

    const predictData = await predictResp.json();
    console.log('Flask /predict response:', JSON.stringify(predictData, null, 2));

    // 3) Shape data for the frontend dashboard
    const names = predictData.available_networks || [];
    const strengths = predictData.network_strength || [];
    const probs = predictData.network_probability_class || [];

    const networks = names.map((name, idx) => ({
      ssid: name,
      strength_class: strengths[idx] != null ? strengths[idx] : 0,
      confidence: probs[idx] != null ? probs[idx] : 0,
      bssid: '',
    }));

    res.json({ networks });
  } catch (err) {
    console.error('Error in /api/scan-and-predict:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});