dl_ver_plus
===========

set the maximum plugin version supported by deadline / 脑残工具合集之2
shitty tools i wrote over the years / 

简单使用法
-----

直接全部复制到X:\DeadlineRepository\scripts\General即可

原理
-----

lz使用了regex(脑残法)来搜索替换已有的plugin的配置文件们(.dlinit / .param / 和submission目录下的.py文件) 这么做没有任何意义，你手改下不就得了，这纯粹是吃饱了撑的，所以lz只做了6,7个plugin的

启动时先使用单独做的dlp package去找到所有的plugins们的版本号，然后显示在界面上，此时可以勾选/取消显示的版本们，滑条默认最大到最后一个版本+10，但是spinbox输入框没有限制，可以随便设),右键菜单可以写设置到配置文件里
