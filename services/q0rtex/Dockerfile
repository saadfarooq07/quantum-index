FROM quay.io/cortexproject/cortex:latest

# Expose the default port
EXPOSE 8000

# Run the binary with HTTP enabled
CMD ["--config.file=/etc/cortex/config.yml", "--server.http-listen-port=8000"]
