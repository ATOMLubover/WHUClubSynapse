FROM docker.io/nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04

ENV MAX_JOBS=16
ENV NVCC_THREADS=4
ENV FLASHINFER_ENABLE_AOT=1
ENV USE_CUDA=1
ENV CUDA_HOME=/usr/local/cuda
ENV TORCH_CUDA_ARCH_LIST='12.0+PTX'
ENV CCACHE_DIR=/root/.ccache
ENV CMAKE_BUILD_TYPE=Release
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
ENV PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" 
ENV PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn" 
# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    kmod \
    git \
    cmake \
    ninja-build \
    build-essential \
    ccache \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip config set global.break-system-packages true
RUN pip install --no-cache-dir --upgrade --ignore-installed pip setuptools wheel --timeout 1200 --retries 10
RUN pip install --no-cache-dir --retries 10 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --timeout 1200
RUN pip install --no-cache-dir modelscope>=1.18.1 --timeout 1200 --retries 10

RUN pip install --no-cache-dir git+https://github.com/facebookresearch/xformers.git@main#egg=xformers --timeout 1200 --retries 10

RUN timeout 1200 git clone https://github.com/bitsandbytes-foundation/bitsandbytes.git /workspace/bitsandbytes
WORKDIR /workspace/bitsandbytes
RUN cmake -DCOMPUTE_BACKEND=cuda -S .
RUN make -j 4
RUN pip install -e . --timeout 1200 --retries 10

# Build flashinfer, set FLASHINFER_ENABLE_AOT=0 for JIT compiler
RUN timeout 1200 git clone https://github.com/flashinfer-ai/flashinfer.git --recursive /workspace/flashinfer
WORKDIR /workspace/flashinfer
RUN pip install --no-cache-dir ninja build packaging "setuptools>=75.6.0" --timeout 1200 --retries 10
RUN python3 -m flashinfer.aot
RUN python3 -m build --no-isolation --wheel
RUN pip install dist/flashinfer*.whl --timeout 1200 --retries 10

RUN pip install aiohttp==3.11.18 --timeout 1200 --retries 10
RUN pip install protobuf==5.29.4 --timeout 1200 --retries 10
RUN pip install click==8.1.8 --timeout 1200 --retries 10
RUN pip install rich==13.7.1 --timeout 1200 --retries 10
RUN pip install starlette==0.46.2 --timeout 1200 --retries 10

# Build vllm
RUN timeout 1200 git clone https://github.com/vllm-project/vllm.git /workspace/vllm
WORKDIR /workspace/vllm
RUN python3 use_existing_torch.py
RUN pip install --no-cache-dir -r requirements/build.txt --timeout 1200 --retries 10
RUN pip install --no-cache-dir setuptools_scm --timeout 1200 --retries 10
RUN python3 setup.py develop

RUN pip install --no-cache-dir accelerate --timeout 1200 --retries 10

# (Optional) If you want to run a shell by default or some other command:
CMD ["bash"]
