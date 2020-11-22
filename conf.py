#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Pan
#
# Created:     05/11/2020
# Copyright:   (c) Pan 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import os
import configparser
#すべてのYP名と数
def yp_names(config):
    try:
        a = (config.options("YP"))
        return(a,len(a))
    except:
        return ("",0)

#個別YPを返す
def get_yp(config,num):
    try:
        a = yp_names(config)[0][num]
        b = config.get("YP",a).split(",")
        return (b)
    except:
        return ()

#タグ用カラーリスト作成
def color_list(config):
    fil = config.options("filter")
    color_list = []
    for ccc in fil:
        ddd = config.get("filter",ccc).split("\\\\")[36]
        color_list.append(ddd)
    return(color_list)

#仮保存
def save_tmp(config):
    f = open("./config.tmp", "w", encoding= 'UTF-8')
    config.write(f)
    f.close()
#仮からロード
def config_tmp(): #キャンセル押した時用
    config = configparser.ConfigParser()
    config.read("./config.tmp", encoding = "UTF-8")
    return(config)

#保存
def save(config):
    f = open("./config.ini", "w", encoding= 'UTF-8')
    config.write(f)
    f.close()
#ロード
def config():
    default_configs = {"SETTING" : {"window_x"   : "480",
                                    "window_y"   : "500",
                                    "position_x" : "100",
                                    "position_y" : "100",
                                    "sort_filter": "True",
                                    "sort_listener" : "True" },
                   "column_size" : {"all"        : "20,20,80,120,80,55,55,55,55,200,150,100"},
                            "YP" : { },
                          "peca" : {"peca_port" : "localhost:7144",
                                    "peca_port2": "",
                                    "update"    : "1",
                                    "timeout"   : "15"},
                        "player" : { },
                          "tool" : { },
                    "set_filter" : {"se"        : "",
                                    "voice"     : "0"},
                        "filter" : { }}

    if os.path.exists("./config.ini"):
        config = configparser.ConfigParser()
        config.read_dict(default_configs)
        config.read("./config.ini", encoding = "UTF-8")
        return(config)
    else:
        config = configparser.ConfigParser()
        config.read_dict(default_configs)
        return(config)
