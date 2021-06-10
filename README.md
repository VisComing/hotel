# 分布式温控系统
## python版本
- 3.8.5
- [可以使用pyenv安装](http://101.200.186.158/2021/06/07/%E5%AE%89%E8%A3%85pyenv/)
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