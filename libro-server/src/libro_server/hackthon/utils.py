import os

def get_record_file_path(file_path):
    # 拆分输入文件路径得到目录和文件名
    dir_name, file_name = os.path.split(file_path)
    
    # 构建目标目录路径（即在原目录下的res子目录）
    res_dir = os.path.join(dir_name, "res")
    
    # 检查目标目录是否存在，如果不存在则创建
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
        print(f"'{res_dir}' directory created.")
    
    # 构建目标文件的完整路径
    res_file_path = os.path.join(res_dir, file_name)
    
    return res_file_path

def get_res_file_path(file_path):
    # 拆分输入文件路径得到目录和文件名
    dir_name, file_name = os.path.split(file_path)
    name = str(file_name).replace('.ipynb','.pickle')
    # 构建目标目录路径（即在原目录下的res子目录）
    res_dir = os.path.join(dir_name, "res")
    
    # 检查目标目录是否存在，如果不存在则创建
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
        print(f"'{res_dir}' directory created.")
    
    # 构建目标文件的完整路径
    res_file_path = os.path.join(res_dir, name)
    
    return res_file_path