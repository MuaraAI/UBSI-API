module.exports = {
  apps: [
    {
      name: "ubsi-api",
      cwd: "/home/ubuntu/ubsi-api",
      script: "/home/ubuntu/.venvs/ubsi-api/bin/uvicorn",
      args: "app.main:app --host 127.0.0.1 --port 8300 --workers 2",
      interpreter: "none",
      autorestart: true,
      max_memory_restart: "150M",
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
