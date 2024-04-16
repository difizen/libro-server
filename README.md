# Libro

## 使用

```sh
pip install libro libro-ai
libro
```

## 开发

本项目包含 lab 目录下的 libro-lab 前端工程和 libro-server、libro-ai 两个 python 包，分别在 libro-server 和 libro-ai 目录下。

### 基础环境

我们使用 rye 来管理多 python 包组成 monorepo，多个包会共享同一个虚拟环境 venv

- install `rye` `npm`
- rye sync

### libro-lab

- cd lab
- npm install
- npm run build
- npm run deploy

### libro-server

- cd libro-server
- npm i
- rye run dev
- rye build
- rye publish

### libro-ai

- cd libro-ai
- rye build
- rye publish

### libro-flow

- cd libro-flowrye sync
- rye build
- rye publish
