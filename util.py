import yaml
import os
from datetime import datetime
import numpy as np
import json

from read import read

def load_config():

    # 加载YAML文件
    if not os.path.isfile("./config.yml"):
        print("error:你的config.yml不存在，请创建，并且这样初始化")
        print("imgs_dir : ")
        return 0
    else:
        with open('./config.yml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        return config

def read_userdata_from_path(img_path):
    """
    从图片的路径中还原出id和name
    input:./users/2210613145_weitong.jpg -> [2210613142,weitong]
    """
    user_data = img_path.split("/")[-1]
    user_id = user_data.split("_")[0]
    user_name = user_data.split("_")[-1].split(".")[0]
    return [user_id,user_name]

def read_users_from_database():
    """
    从database中读取数据，并且转换成
    {id:,name:,features:}
    """
    users_data = []
    rows = read()
    for row in rows:
        feature_str = row[2]
        feature_arrary = np.array(json.loads(feature_str))
        # print(feature_arrary)
        # print(type(feature_arrary),feature_arrary.shape)
        users_data.append({"id":row[0],"name":row[1],"features":feature_arrary})
    return users_data

def save_file(id,name):
    """
    输入id,name,输出保存路径。
    """
    config = load_config()
    save_dir = config["imgs_dir"]
    img_name = id + "_" + name
    save_file_path = save_file+img_name
    return save_file_path

def custom_round(value):
    """
    将特征向量压到4位小数。
    """
    # 将值四舍五入到小数点后两位
    rounded_value = round(value, 4)
    # 如果四舍五入后的值是 0，则返回 0.00001
    if rounded_value == 0:
        return 0.00001
    return rounded_value
