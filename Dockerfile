# 使用 python 3.11 作为基础镜像
FROM python:3.11-slim-bookworm

# 安装 libro 包
RUN pip install libro

