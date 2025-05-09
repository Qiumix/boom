# 项目介绍

命令行扫雷，利用ansi转移序列实现命令行的各种效果
## 无缓冲输入

windows利用visual c++的getch实现无缓冲输入
类unix系统则是termios和tty库实现
利用高阶函数封装平台判定过程
## ansi转义序列与抽象屏障

使用跨平台库colorama，这是一个对ansi转义序列进行封装的库，使用方便
ansi转义序列：\0x1b也即\033开头，对应ascii码ESC，加一个[和特定的字符组合实现特定功能转义
例如2K清行，已经被封装在colorama库的clear_line里了
利用lambda函数星号表达式实现对print的默认参数更改->cout
大部分序列由列表推导式创建
通过将ansi转义序列与cout的封装在一起实现清行清屏移动等功能，构成了第一层抽象屏障
print_all和show_relevant(调用show_col show_line), clear_bg, print_boom等函数调用封装了ansi转移序列的函数，实现第二层抽象屏障
print_message对cout和cline进行封装，可以打印按键和错误信息
## 逻辑实现

### 获取按键

get_key函数如果获取到数字键就存入缓冲区，然后打印缓冲区，识别到其他按键就将缓冲区和该按键同时打印并清空缓冲区，当识别到退格键会将缓冲区整除十，并不打印退格键
如果按键出现异常，则会抛出异常并打印错误
### 移动光标

会判定缓冲区数字与获得的按键，若是reveal和flag行为则不考虑缓冲区，否则行为为进行**缓冲区数字次**位置移动，这个过程并非一个一个格子移动，而是通过move_cursor_info函数获得移动后的位置(同时通过内置的max与min函数判定是否越界)，调用clear_bg清除原格子背景高亮，再用show_relevant函数高亮移动后的位置并显示相对行号
### 揭开某个格子

首先判定当前格子是否已经revealed或者flaged，若为True则直接return不做处理，否则判定是否是炸弹，若为True则返回is_boomed为True，由主循环处理
最后利用内层函数inner进行dfs，越界等特殊情况直接return，否则执行递归主体
因为修改的三个变量都是可变序列，类似c语言的引用传参，执行完inner直接返回即可

