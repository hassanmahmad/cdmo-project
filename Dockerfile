FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1 \
    libxkbcommon0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Install MiniZinc
RUN wget https://github.com/MiniZinc/MiniZincIDE/releases/download/2.9.1/MiniZincIDE-2.9.1-bundle-linux-x86_64.tgz -O minizinc.tgz && \
    tar -xzf minizinc.tgz && \
    mv MiniZincIDE-2.9.1-bundle-linux-x86_64 /opt/minizinc && \
    ln -s /opt/minizinc/bin/minizinc /usr/local/bin/minizinc && \
    rm minizinc.tgz

RUN pip3 install z3-solver pulp

# set pwd
WORKDIR /app

# Copy files
COPY source/ /app/source/
COPY solution_checker.py /app/
COPY run_all.py /app/

# Create results directories
RUN mkdir -p /app/res/CP /app/res/SMT /app/res/MIP

# command
CMD ["python3", "run_all.py"]