# 分布式温控系统
## 使用GIT协作
- 克隆代码库 `git clone git@gitee.com:adslppp/hotel-air-conditioner.git`
### 如何提交代码
我们采用code review形式提交代码
首先，新建一个分支，分支命名方式:名字缩写_日期_内容，比如zrf_0609_PRtest
`git checkout -b zrf_0609_PRtest`
这会创建一个新分支，并切换到新分支上。
然后，在新分支上书写代码并提交 `git push --set-upstream origin zrf_0609_PRtest`
当push之后，来到gitee的Pull Request界面，新建Pull Request
源分支选择你新建的分支，目标分支选择master
创建之后，等待同学的评审，评审通过后就会把你的分支合入master分支了。