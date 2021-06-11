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
### 将pyenv添加进环境变量
```
echo -e 'if shopt -q login_shell; then' \
      '\n  export PYENV_ROOT="$HOME/.pyenv"' \
      '\n  export PATH="$PYENV_ROOT/bin:$PATH"' \
      '\n eval "$(pyenv init --path)"' \
      '\nfi' >> ~/.bashrc

echo -e 'if [ -z "$BASH_VERSION" ]; then'\
      '\n  export PYENV_ROOT="$HOME/.pyenv"'\
      '\n  export PATH="$PYENV_ROOT/bin:$PATH"'\
      '\n  eval "$(pyenv init --path)"'\
      '\nfi' >>~/.profile
```
### 重启shell或者source
- `source ~/.bashrc`
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
## 新建分支
- 你对代码的任何更改都要建立新分支
- 分支名命名规则：姓名首拼_日期_分支描述，如`zrf_0611_initProject`
- 新建分支
    - 确保自己在master分支上
    - 拉取最新的master
    - 新建分支 `git ckeckout -b zrf_0611_initProject`
    - 更改代码，add、commit
    - push时注意将本地分支推送到远端 `git push --set-upstream origin zrf_0611_initProject`
    - 在gitee新建pull request
    - 等待负责人评审

## IDE
- 推荐使用vscode
- vscode插件推荐：python、MySQL(3.8.7)、gitlens

## peewee教程
- 首先import你准备操作的model，比如`from src.model.Order import Order`，这样就把Order类导入了
- 导入DBManager，`from src.model.BaseModel import DBManager`
- 参考peewee-async[官方文档](https://peewee-async.readthedocs.io/en/latest/peewee_async/api.html#manager)
