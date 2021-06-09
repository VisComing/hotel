# 判断python版本是否为3.8.5
# 如果不是安装pyenv python3.8.5
pyVersion=`python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'`
expectVersion="3.8.5"
if [ "$pyVersion" != "$expectVersion" ]
then
    # 安装pyenv，安装python3.8.5
    sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

    git clone https://github.com.cnpmjs.org/pyenv/pyenv.git ~/.pyenv
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
    wget https://npm.taobao.org/mirrors/python/3.8.5/Python-3.8.5.tar.xz -P ~/.pyenv/cache/;pyenv install 3.8.5
    pyenv global 3.8.5
fi

pip3 install -r requirements.txt
pre-commit install