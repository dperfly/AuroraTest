#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Zeta_Byte_Network_Security_Interface 
@File    ：clean_files.py
@IDE     ：PyCharm 
@Author  ：萌新小缘
@Date    ：2024/6/13 14:06 
"""
import os


def del_file(path):
    """删除目录下的文件"""
    list_path = os.listdir(path)
    for i in list_path:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
