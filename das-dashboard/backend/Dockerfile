FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    docker.io \
    bash-completion \
    dpkg \
    && rm -rf /var/lib/apt/lists/*

# fake systemctl
RUN ln -sf /bin/true /usr/bin/systemctl

# install package
RUN dpkg -i ./das-toolbox_1.0.7_amd64.deb

RUN mkdir -p /runtime_keys \
    /opt/das/.das \
    && chmod 700 /runtime_keys

ENV HOME=/opt/das

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "main:dashboard_app", "--host", "0.0.0.0", "--port", "8000"]