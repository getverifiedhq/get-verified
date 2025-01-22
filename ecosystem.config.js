module.exports = {
  apps: [
    {
      name: "get-verified",
      script: "python3.10",
      args: "src/app.py",
      instances: 1,
      watch: true,
    },
  ],
};
