# HTTP核心概念笔记

## 什么是HTTP
HTTP是浏览器/程序和服务器之间：“说话”用的语言规则。
你每次打开一个网页，就是浏览器用HTTP向服务器“要”内容。

##请求（Request）
你>服务器，包含：
 方法（Method）：你要做什么
 GET：获取数据（比如查看文章列表）
 POST：提交数据（比如发表评论）
 PUT：更新数据（比如修改用户名）
 DELETE：删除数据（比如删除一篇文章）
 URL：你要访问哪个地址
 Headers：附加信息（比如你的身份token）
 Body：你携带的数据（GET请求通常没有body，POST请求通常有）

 ##响应（Response）
 服务器>你，包含：
 状态码（Status Code）：结果怎么样
  200：成功
  201：创建成功（POST请求成功时常见）
  400：你的请求有问题（比如参数格式错误）
  401：没有权限（没登录或token无效）
  404：找不到（你访问的资源不存在）
  500：服务器出错
Headers：附加信息
Body：返回的数据（通常是JSON格式）

## 什么是JSON格式
JSON是一种数据格式，长这样：
{
    "name":"小明",
    "age":"20",
    "skills":["Python","FastAPI"]
}
Python里的字典/列表和JSON可以互相转换（json.dumps/json.loads）。

##什么是API
API是服务器对外暴露的“操作入口”，比如：
GET   /todos >获取所有待办事项
POST  /todos >新建一条待办事项
PUT   /todos/{id} >更新id对应的待办事项
DELETE /todos/{id} >删除id对应的待办事项
这种设计分格叫做 REST API,是目前最主流的API设计方式。