import os
import shutil


def root_path():
    """ 获取根路径 """
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return path


def data_path():
    """ 获取数据路径 """
    path = os.path.join(root_path(), "testcase")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def log_path():
    """ 获取日志路径 """
    path = os.path.join(root_path(), "logs")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def report_path():
    """ 获取报告路径 """
    path = os.path.join(root_path(), "report")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def copy_dir_file(src_dir, dst_dir):
    """
    从src_dir拷贝文件到dst_dir
    """
    for filename in os.listdir(src_dir):
        src_file_path = os.path.join(src_dir, filename)  # 源文件的完整路径
        dst_file_path = os.path.join(dst_dir, filename)  # 目标文件的完整路径

        # 检查是否为文件，避免复制子目录
        if os.path.isfile(src_file_path):
            try:
                # 复制文件，覆盖目标目录中的同名文件
                shutil.copy2(src_file_path, dst_file_path)  # 可以使用 copy() 若不需要保留元数据
            except Exception as e:
                raise f"复制文件 {src_file_path} 时出错: {e}"


def get_all_files(file_path, yaml_data_switch=False) -> list:
    """
    获取文件路径
    :param file_path: 目录路径
    :param yaml_data_switch: 是否过滤文件为 yaml格式， True则过滤
    :return:
    """
    filename = []
    # 获取所有文件下的子文件名称
    for root, dirs, files in os.walk(file_path):
        for _file_path in files:
            path = os.path.join(root, _file_path)
            if yaml_data_switch:
                if 'yaml' in path or '.yml' in path:
                    filename.append(path)
            else:
                filename.append(path)
    return filename


def pictures_path():
    """ 获取图片路径 """
    path = os.path.join(report_path(), "picture")
    if not os.path.exists(path):
        os.makedirs(path)
    return path
