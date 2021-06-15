# 分布式温控系统
## 系统环境
- ubuntu 18.04
- 当然，你也可以使用Windows

## python版本
- 3.8.5
- [可以使用pyenv安装](http://101.200.186.158/2021/06/07/%E5%AE%89%E8%A3%85pyenv/)
## 使用pyenv安装python3.8.5
## 安装pyenv
### 安装构建python的依赖
```bash
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
### clone pyenv代码库
- `git clone https://github.com.cnpmjs.org/pyenv/pyenv.git ~/.pyenv`
### [将pyenv添加进环境变量](https://github.com/pyenv/pyenv#basic-github-checkout)
这两行放在~/.profile的开头
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
```
这一行放在~/.profile结尾
```
eval "$(pyenv init --path)"
```
### 重启shell或者source
- `source ~/.profile`
### 下载安装python3.8.5
- `v=3.8.5;wget https://npm.taobao.org/mirrors/python/$v/Python-$v.tar.xz -P ~/.pyenv/cache/;pyenv install $v`
### 使python3.8.5生效
- `pyenv global 3.8.5`
## 克隆项目
- `git clone git@gitee.com:adslppp/hotel-air-conditioner.git`
- `cd hotel-air-conditioner`
## 安装`requirementlists`
- `pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
## git钩子
- 在你执行git commit时，会先执行black，格式化代码
- 如果black后更新了你的代码，那么被更新的代码不会自动添加到暂存区，需要你手动add进去
- 执行black时可能会报错，大概率是你的代码有问题，需要修改一下
- 建议commit之前手动执行`black ./`
## 配置pre-commit
- `pre-commit install`
## Pull Request
- 你对代码的任何更改都要建立新分支
- 分支名命名规则：姓名首拼_日期_分支描述，如`zrf_0611_initProject`
- 新建分支
    - 方式一：本地新建分支
        - 确保自己在master分支上
        - 拉取最新的master
        - 新建分支 `git checkout -b zrf_0611_initProject`
        - 更改代码，add、commit
        - push时注意将本地分支推送到远端 `git push --set-upstream origin zrf_0611_initProject`
    - 方式二：远程新建
        - 在gitee上新建一个分支，注意以master为起点
        - `git fetch --all`
        -  `git checkout -b zrf_0611_initProject origin/zrf_0611_initProject`
- 在gitee新建pull request
    - 源分支选择你创建的分支
    - 目标分支选择master
- 等待负责人评审

## IDE
- 推荐使用vscode
- vscode插件推荐：python、MySQL(3.8.7)、gitlens
- Python Docstring Generator 用于快速生成函数注释模板
    - 在该插件的设置里勾选上 `Auto Docstring: Include Name`

## peewee教程
- 首先import你准备操作的model，比如`from src.model.Order import Order`，这样就把Order类导入了
- 导入DBManager，`from src.model.BaseModel import DBManager`
- 参考peewee-async[官方文档](https://peewee-async.readthedocs.io/en/latest/peewee_async/api.html#manager)
- 参考peewee[官方文档](http://docs.peewee-orm.com/en/latest/peewee/querying.html#)

## 数据库
- mysql
- 你需要创建一个hotel数据库 `create database hotel;`
- 你可以更改本地连接数据库的配置信息，在`src/settings.py`中的`MySQLDatabaseConfig`进行修改

## jsonrpc/websockets
- [参考文档](https://beau.click/jsonrpc/websockets)
- [如何返回错误](https://jsonrpcserver.readthedocs.io/en/latest/api.html#errors)

## 如何测试
- 需要你自己写一个client，参考协议，向服务器发送一段数据，看服务器会输出什么
```python
import asyncio
import logging
import websockets
from jsonrpcclient.clients.websockets_client import WebSocketsClient

async def main():
    async with websockets.connect("ws://localhost:18000") as ws:

        async def sendMsg():
            response = await WebSocketsClient(ws).request(
                "createOrder", userID="Alice", roomID="01-01-02"
            )
            logging.info(response.data.result)
        await sendMsg()

asyncio.get_event_loop().run_until_complete(main())
```
