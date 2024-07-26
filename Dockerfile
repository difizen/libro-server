# 使用 python 3.11 作为基础镜像
FROM python:3.11-slim-bookworm

# 安装 libro 包
RUN pip install libro
RUN mkdir -p ~/.jupyter
COPY docker/jupyter_server_config.py ~/.jupyter/jupyter_server_config.py

CMD ["libro", '--port', '8889']