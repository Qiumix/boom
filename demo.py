def make_getch():
    """创建并返回适用于当前平台的单字符读取函数"""
    import os

    # Windows平台实现
    if os.name == 'nt':
        import msvcrt
        
        def getch_windows():
            """Windows系统的getch实现"""
            first_char = msvcrt.getch()
            
            # 处理方向键（两字节序列）
            if first_char in (b'\xe0', b'\x00'):
                second_char = msvcrt.getch()
                # Windows方向键映射表
                key_mapping = {
                    b'H': '^',  # 上
                    b'P': 'v',  # 下
                    b'K': '<',  # 左
                    b'M': '>',  # 右
                }
                return key_mapping.get(second_char, second_char.decode())
                
            return first_char.decode('ascii', errors='replace')
        
        return getch_windows

    # 类Unix系统实现
    else:
        import sys
        import termios
        import tty
        
        def getch_unix():
            """类Unix系统的getch实现"""
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
                
                # 处理方向键（三字节序列）
                if char == '\x1b':  # ESC
                    if sys.stdin.read(1) == '[':
                        third = sys.stdin.read(1)
                        # Unix方向键映射表
                        key_mapping = {
                            'A': '^',  # 上
                            'B': 'v',  # 下
                            'C': '>',  # 右
                            'D': '<',  # 左
                        }
                        return key_mapping.get(third, third)
                return char
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        return getch_unix

# 创建适合当前平台的getch函数
getch = make_getch()