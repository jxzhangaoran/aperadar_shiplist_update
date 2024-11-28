import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 获取当前文件所在目录的父级目录
parent_directory = os.path.dirname(current_directory)
# 获取当前文件所在目录的爷爷级别目录
grandparent_directory = os.path.dirname(parent_directory)
# 获取当前文件所在目录的曾祖父级别目录
great_grandparent_directory = os.path.dirname(grandparent_directory)
# 路径拼接
# os.path.join(current_directory, "xxx")