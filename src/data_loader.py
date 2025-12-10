import pandas as pd

def load_data(file_path):
    """
    加载并清洗数据
    :param file_path: 数据文件路径
    :return: 处理后的 DataFrame
    """
    # 加载 CSV 文件
    data = pd.read_csv(file_path)
    
    # 数据清洗（处理缺失值、数据类型转换等）
    data.fillna(0, inplace=True)  # 填充缺失值
    data['ctr'] = data['click'] / data['impr']  # 计算 CTR
    
    return data