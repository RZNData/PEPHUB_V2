module.exports = {
  apps: [
    {
      name: "pephub-whatsapp-bot",
      script: "bot.js",
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      restart_delay: 3000,
      exp_backoff_restart_delay: 200,
      max_restarts: 50,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PYTHONIOENCODING: "utf-8",
      },
      error_file: "logs/error.log",
      out_file: "logs/out.log",
      merge_logs: true,
      time: true,
    },
  ],
};
