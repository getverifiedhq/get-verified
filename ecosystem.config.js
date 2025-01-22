module.exports = {
  apps: [
    {
      name: "get-verified",
      script: "src/app.py",
      interpreter: "./myenv/bin/python",
      instances: 1,
      watch: true,
    },
  ],
};
