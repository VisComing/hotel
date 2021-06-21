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
- `git clone git@github.com:VisComing/hotel.git`
- `cd hotel`
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

~~## 如何测试~~
- 需要你自己写一个client，参考协议，向服务器发送一段数据，看服务器会输出什么
- 发送一个notify
```python
import asyncio
import logging
import websockets
from jsonrpcclient.clients.websockets_client import WebSocketsClient

async def main():
    async with websockets.connect("ws://localhost:18001") as ws:

        async def sendMsg():
            await WebSocketsClient(ws).notify(
                "PowerOn", roomID="01-01-02"
            )
        await sendMsg()

asyncio.get_event_loop().run_until_complete(main())
```

## 单元测试
- 单元测试是必须的
- 你每完成一个函数，都要对该函数进行单测
- 测试框架，pytest `pip3 install pytest-asyncio`
- 测试文件命名，以`test_`开头
- 可以参考我已经写好的`test_createOrder.py`
- 运行测试，如果使用的是vscode的话那么可以在左侧选项栏中找到测试(前提是你安装了python插件)。
- 也可以在命令行中执行, 输入`pytest`就会自动执行测试
- 如果测试过程中需要对数据库操作，那么新建一个数据库，名字为`mock_hotel`
- test目录下`Utils.py`有个`initDB`函数,该函数会新建表，删除表里面的内容，并且初始化几个Device
- 如果使用Windows系统，多次执行createTables函数(initDB中调用)会报错，那么只执行一次就可以了，然后你把这个函数注释掉
- 如果vscode左侧没有显示测试的拓展，可以试试按`ctrl + shift + p`，输入`configure tests`，配置一下python测试框架，选择pytest

## 持续集成
- 当提交代码后，会自动执行单元测试，确保你此次提交的代码不会影响之前的代码
- 当代码推到master分支后，会进行自动部署，自动计算覆盖率

## 持续部署
- IP：101.200.186.158
- admin端口：18000
- client端口：18001

## 代码覆盖率
- cov.zhouruifa.top
- 可以查看你写的代码哪个部分被测试覆盖到了，哪个部分没有覆盖到
- 目前覆盖率功能还不完善，只有全量覆盖率，并且只计算了master分支的代码
- 目前还没有配置增量覆盖率
