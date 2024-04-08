# Libro

## 使用

```sh
pip install libro libro-ai
libro
```


## 开发

本项目包含lab目录下的libro-lab前端工程和libro-server、libro-ai两个python包，分别在libro-server和libro-ai目录下。

### libro-lab

- npm install
- npm run build
- npm run deploy

### python

我们使用rye来管理多python包组成monorepo，多个包会共享同一个虚拟环境venv

- install `rye` `npm`
- cd libro-server
- rye sync

### libro-server

- cd libro-server/libro-server
- npm i
- rye run dev
- rye build
- rye publish

### libro-ai

- cd libro-ai/libro-ai
- rye build
- rye publish
