# b站分布式爬虫V1.0
[b站](https://www.bilibili.com/)
爬虫将对b站的视频，用户，评论，标签，文章, 在线人数进行抓取。

### 功能
**1. 根据redis中存入的url进行规则匹配，执行相应的爬取功能。**
2. 定时抓取在线人数，通过开启扩展来设置。
3. 接受get形式的url，并在相应的视频下进行评论。

### 使用
1. 设置: **参考settings.py中的相应配置**
2. url规则: 
 * 视频: 接受https://www.bilibili.com/video/av+av号/的url, 将对该video进行抓取。
 * 文章: 接受https://www.bilibili.com/read/cv+cv号/的url, 将对该article进行抓取。
 * 用户: 接受https://space.bilibili.com/mid号/的url, 将对该user进行抓取。该方法需要登录cookies
 * 标签: 接受https://www.bilibili.com/tag/id号/的url, 将对该tag进行抓取。
 * 回复: 接受https://www.bilibili.com/reply加get参数的url, 该方法需要登录cookies 
 _参数配置:_
   1. _oid_: av号
   2. _message_: 你想回复的信息内容
      
3. 扩展: 在settings.py中EXTENSION打开需要的扩展