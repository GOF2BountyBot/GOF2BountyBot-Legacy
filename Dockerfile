# Below should always be the latest LTS release
ARG UBUNTU_RELEASE=24.04
# Below should be a reasonably current Cuda version
ARG CUDA_VERSION=12.8.1


FROM nvidia/cuda:${CUDA_VERSION}-cudnn-devel-ubuntu${UBUNTU_RELEASE} AS base



ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda-12.8
ENV PATH=/opt/venv/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/opt/venv/

# Update cuda apt repo
RUN apt-key del 7fa2af80 && \
    sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list.d/* && \
    sed -i '/developer\.download\.nvidia\.com\/compute\/machine-learning\/repos/d' /etc/apt/sources.list.d/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wget && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb && \
    dpkg -i cuda-keyring_1.1-1_all.deb 

# Install system dependencies and Python
RUN echo 'tzdata tzdata/Areas select Etc' | debconf-set-selections; \
    echo 'tzdata tzdata/Zones/Etc select UTC' | debconf-set-selections; \
    apt-get update && \
    apt-get --with-new-pkgs upgrade -y && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        autoconf \
        apt-utils \
        pkg-config && \
    # Add deadsnakes ppa for added python versions
    add-apt-repository ppa:deadsnakes/ppa
        
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        git \
        python3-pip \
        python3.10-dev \
        python3.10-venv \
        libpython3.10-dev \
        openssl \
        # Extras for BountyBot
        postgresql-client \
        blender \
        g++-14 \
        gcc-14&& \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --config python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create a virtual environment
RUN python3.10 -m venv /opt/venv

WORKDIR /app/BountyBot

# Copy requirements file
COPY requirements.txt .

# Activate the virtual environment and upgrade pip
RUN chmod +x /opt/venv/bin/activate && \
    /opt/venv/bin/pip install --upgrade --no-cache-dir \
        pip \
        setuptools \
        wheel  \
        ninja \
        meson
        
# Install dependencies
RUN /opt/venv/bin/pip install --upgrade --no-cache-dir --prefer-binary -r requirements.txt

# Copy remaining app code...
COPY . .

# create a non-root user
RUN groupadd --gid 1002 botuser && \
    useradd --uid 1001 --gid botuser --shell /bin/bash --create-home botuser && \
    chown -R botuser /home/botuser && \
    chown -R botuser /app/BountyBot && \
    chmod -R 1777 /home/botuser && \
    chmod -R 1777 /app/BountyBot


USER botuser

ENTRYPOINT ["/bin/bash", "-c", "source /opt/venv/bin/activate && /opt/venv/bin/python main.py & tail -f /dev/null"]
