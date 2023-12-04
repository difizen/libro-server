# libro server

## env setup

install python >=3.8

install poetry # 更好的包管理器

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

进入 python 虚拟环境，安装依赖包

```sh
cd ./python-packages/libro-server
poetry shell
poetry install
```

## dev

启动开发服务器，配合 libro 前端的 demo 调试和 libro-app 开发

```sh
# open libro server in dev mode
poe dev
# open jupyter lab in dev mode
poe lab
```

Libro Server 默认使用基于 [libro-lab](https://github.com/difizen/libro/tree/main/packages/libro-lab) 的前端应用，作为前端静态资源

## pub

```sh
rm -rf dist
poetry build
twine upload dist/*
```
