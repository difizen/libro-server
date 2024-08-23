# 使用 python 3.11 作为基础镜像
FROM python:3.11-slim-bookworm

RUN mkdir -p /root/.jupyter

COPY docker/jupyter_server_config.py /root/.jupyter/jupyter_server_config.py

COPY dist/libro-0.1.11-py3-none-any.whl /libro-0.1.11-py3-none-any.whl
COPY dist/libro_flow-0.1.2-py3-none-any.whl /libro_flow-0.1.2-py3-none-any.whl
COPY dist/libro_ai-0.1.4-py3-none-any.whl /libro_ai-0.1.4-py3-none-any.whl

# 安装 libro 包
RUN pip install /libro_flow-0.1.2-py3-none-any.whl
RUN pip install /libro_ai-0.1.4-py3-none-any.whl
RUN pip install /libro-0.1.11-py3-none-any.whl

RUN mkdir -p /config

# 创建 .ipython/profile_default/startup/ 目录
RUN mkdir -p ~/.ipython/profile_default/startup/
# 创建启动脚本，自动加载 libro_ai 扩展
RUN echo "get_ipython().run_line_magic('load_ext', 'libro_ai')" > ~/.ipython/profile_default/startup/load_libro_ai.py

WORKDIR /userdata

CMD ["libro","--port","8889","--allow-root"]