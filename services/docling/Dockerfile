FROM continuumio/miniconda3:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create conda environment
COPY environment.yml .
RUN conda env create -f environment.yml && \
    conda clean -afy

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "quantum-env", "/bin/bash", "-c"]

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the FastAPI server
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "quantum-env"]
CMD ["uvicorn", "cortex_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
