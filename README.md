# libro server

## env setup

install python >=3.8

install poetry # 更好的包管理器

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

进入 python 虚拟环境，安装依赖包

```sh
cd libro_server
poetry shell
poetry install
```

## dev

启动开发服务器

```sh
# open libro server in dev mode
poe dev
```

Libro Server 默认使用基于 [libro-lab](https://github.com/difizen/libro/tree/main/packages/libro-lab) 的前端应用，作为前端静态资源

## pub

```sh
rm -rf dist
poetry build
twine upload dist/*
```
