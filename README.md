dl_ver_plus
===========

set the maximum plugin version supported by deadline
shitty tools i wrote over the years / 脑残工具合集之2

![Imgur](http://i.imgur.com/TT9Ek7P.png)

![Imgur](http://i.imgur.com/mgYybwf.png)

简单使用方法
-----

直接全部复制到X:\DeadlineRepository\scripts\General即可

原理
-----

lz使用了regex(脑残法)来搜索替换已有的plugin的配置文件们(.dlinit / .param / 和submission目录下的.py文件) 这么做没有任何意义，你手改下不就得了，这纯粹是吃饱了撑的，所以lz只做了6,7个plugin的

启动时先使用单独做的dlp package去找到所有的plugins们的版本号，然后显示在界面上，此时可以勾选/取消显示的版本们，滑条默认最大到最后一个版本+10，但是spinbox输入框没有限制，可以随便设),右键菜单可以写设置到配置文件里

围观lz脑抽过程戳[这里](https://ilmvfx.wordpress.com/2014/06/21/deadline-5-2-how-to-add-latest-maya-version-2015-support-in-submitter-ui-and-plugin-configuration-ui-zhuangbility/?preview=true&preview_id=3729&preview_nonce=6e2684990a)(墙外 请自助)
