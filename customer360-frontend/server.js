/**
 * Node.js Static Server for Customer 360 Frontend
 * Zero external dependencies - runs with pure Node.js runtime.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

const MIME_TYPES = {
    '.html': 'text/html; charset=UTF-8',
    '.css': 'text/css; charset=UTF-8',
    '.js': 'application/javascript; charset=UTF-8',
    '.json': 'application/json; charset=UTF-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    // Sanitize URL to avoid directory traversal
    let safeUrl = req.url.split('?')[0];
    if (safeUrl === '/' || safeUrl === '') {
        safeUrl = '/index.html';
    }

    const filePath = path.join(PUBLIC_DIR, safeUrl);

    // Check if file is within PUBLIC_DIR
    if (!filePath.startsWith(PUBLIC_DIR)) {
        res.writeHead(403, { 'Content-Type': 'text/plain; charset=UTF-8' });
        res.end('403 Forbidden');
        return;
    }

    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            // Fallback to index.html for SPA client-side routing
            const fallbackPath = path.join(PUBLIC_DIR, 'index.html');
            fs.readFile(fallbackPath, (fallbackErr, data) => {
                if (fallbackErr) {
                    res.writeHead(404, { 'Content-Type': 'text/plain; charset=UTF-8' });
                    res.end('404 Not Found');
                    return;
                }
                res.writeHead(200, { 'Content-Type': 'text/html; charset=UTF-8' });
                res.end(data);
            });
            return;
        }

        const ext = path.extname(filePath).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';

        fs.readFile(filePath, (readErr, content) => {
            if (readErr) {
                res.writeHead(500, { 'Content-Type': 'text/plain; charset=UTF-8' });
                res.end('500 Internal Server Error');
                return;
            }

            res.writeHead(200, {
                'Content-Type': contentType,
                'Cache-Control': 'no-cache'
            });
            res.end(content);
        });
    });
});

server.listen(PORT, () => {
    console.log('=================================================');
    console.log(` Customer 360 Frontend Server (Node.js)`);
    console.log(` Running at: http://localhost:${PORT}`);
    console.log(` Press Ctrl+C to stop.`);
    console.log('=================================================');
});
