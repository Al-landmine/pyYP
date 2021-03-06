#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Pan
#
# Created:     11/11/2020
# Copyright:   (c) Pan 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import datetime
import html
import requests
import re
import gc

import conf

def update_t():
    return(update)

def get_list():
    return(all_list)

#チャンネル取得                　
def get_ch(config,names):
    global flg
    global res
    if flg != 0:
        return
    flg = 1
    res = []
    for i in range(conf.yp_names(config)[1]):
        tmp = conf.get_yp(config,i)
        res.append(i)
        try:
            payload = {'host':config.get("peca","peca_port")}
            headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1)","Cache-Control":"no-cache","Accept-Encoding":"identity"}
            res[i] = requests.get(tmp[1]+"index.txt",params=payload, headers=headers,timeout = int(config.get("peca","timeout")))
            res[i].encoding = "utf-8"
            print(tmp[0],":",res[i])
        except:
            print("error" )
    search(config,names)


# 0 チャンネル名<> 1 ID<> 2 TIP<> 3 コンタクトURL<> 4 ジャンル<> 5 詳細<>
# 6 リスナー数<> 7 リレー数<> 8 ビットレート<> 9 タイプ<> 10 アーティスト<>
# 11 タイトル<> 12 アルバム<> 13 URL2<> 14 チャンネル名（エンコ済み）<>
# 15 配信時間<> 16 ステート<> 17 コメント<> 18 ダイレクト接続
#　後から付加した分
# 19 YP名 20 新着記号 21 フィルタ+背景色 22 すべてタブに表示
# 23 ブラックリスト 24 SEフラグ 25 filter_tag
def search(config,names):
    global all_list
    global update
    global flg

    all_list = []
    for n in range(conf.yp_names(config)[1]):
        try:
            if str(res[n]) != "<Response [200]>":   #正常に拾えてなかったらスキップ
                all_list.append("")
                continue
        except:                                     #設定のタイミングによってエラーが出てしまう、何とかこれで吸収してくれ
            flg = 0
            return
        if conf.get_yp(config,n)[2] == "True":
            add = "True"
        else:
            add = "False"
        tmp = conf.get_yp(config,n)             #YPごとに分離
        yy = res[n].text.split("\n")            #チャンネルごとに分離
        list = []

        for m in range(len(yy)):                #各チャンネルをリスト型に再構築
            pp = yy[m].split("<>")

            if len(pp) < 18:                    #ゴミがあったらスキップ
                continue

            try:                                #リスナー数をint型に
                pp[6] = int(pp[6])
            except:
                pp[6] = 0

            pp.append(tmp[0])                   #YP名付加(19)

            if pp[0] in names[n]:               #新着チェック符号付加(20)
                pp.append("")
            else:
                pp.append("◎")

            #フィルター処理
            pp.append("")               #フィルタ判定　ヒットすれば背景色(21)
            pp.append(add)              #すべてタブに表示　フラグ (22)
            pp.append("")               #ブラックリスト　フラグ (23)
            pp.append("")               #SEフラグ(24)
            pp.append("")               #filter_tag(25)
            for ser in config.options("filter"):
                ward = config.get("filter",ser).split("\\\\")
                if ward[37] == "0":
                    continue
                if ward[39] == "1":     #NOT
                    rif = ""
                    if ward[23] == "1":
                        rif += pp[0] + " "
                    if ward[24] == "1":
                        rif += pp[4] + " "
                    if ward[25] == "1":
                        rif += pp[5] + " "
                    if ward[26] == "1":
                        rif += pp[17] + " "
                    if ward[27] == "1":
                        rif += pp[10] + " "
                    if ward[28] == "1":
                        rif += pp[11] + " "
                    if ward[29] == "1":
                        rif += pp[12] + " "
                    if ward[30] == "1":
                        rif += pp[19] + " "
                    if ward[31] == "1":
                        rif += pp[3] + " "
                    if ward[32] == "1":
                        rif += pp[9] + " "
                    rif = rif.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                    check = ward[2].translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                    m = re.search(check, rif,flags=re.IGNORECASE)
                    if str(m) != "None":
                        continue

                rif = ""                #AND1
                if ward[0] != "":
                    if ward[3] == "1":
                        rif += pp[0] + " "
                    if ward[4] == "1":
                        rif += pp[4] + " "
                    if ward[5] == "1":
                        rif += pp[5] + " "
                    if ward[6] == "1":
                        rif += pp[17] + " "
                    if ward[7] == "1":
                        rif += pp[10] + " "
                    if ward[8] == "1":
                        rif += pp[11] + " "
                    if ward[9] == "1":
                        rif += pp[12] + " "
                    if ward[10] == "1":
                        rif += pp[19] + " "
                    if ward[11] == "1":
                        rif += pp[3] + " "
                    if ward[12] == "1":
                        rif += pp[9] + " "
                    rif = rif.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                    check = ward[0].translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                    m = re.search(check, rif,flags=re.IGNORECASE)

                    if str(m) != "None":
                        if ward[38] == "0":

                            pp[21] = ward[36]   #背景色
                            pp[25] = str(ser)   #フィルタ名付加
                            if ward[33] == "1": #すべてタブに乗せる
                                pp[22] = "True"
                            if ward[35] == "1": #ブラックリスト
                                pp[23] = "True"
                            if ward[34] == "1": #SE
                                pp[24] = "True"
                        else:
                            if ward[38] == "1": #AND2
                                rif = ""
                                if ward[13] == "1":
                                    rif += pp[0] + " "
                                if ward[14] == "1":
                                    rif += pp[4] + " "
                                if ward[15] == "1":
                                    rif += pp[5] + " "
                                if ward[16] == "1":
                                    rif += pp[17] + " "
                                if ward[17] == "1":
                                    rif += pp[10] + " "
                                if ward[18] == "1":
                                    rif += pp[11] + " "
                                if ward[19] == "1":
                                    rif += pp[12] + " "
                                if ward[20] == "1":
                                    rif += pp[19] + " "
                                if ward[21] == "1":
                                    rif += pp[3] + " "
                                if ward[22] == "1":
                                    rif += pp[9] + " "
                                rif = rif.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                                check = ward[1].translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                                m = re.search(check, rif,flags=re.IGNORECASE)
                                if str(m) != "None":
                                    pp[21] = ward[36]   #背景色
                                    pp[25] = str(ser)   #フィルタ名付加
                                    if ward[33] == "1":
                                        pp[22] = "True"
                                    if ward[35] == "1": #ブラックリスト
                                        pp[23] = "True"
                                    if ward[34] == "1": #SE
                                        pp[24] = "True"

            if pp[23] != "True":    #ブラックリストじゃなければ再リスト化
                list.append(pp)

        all_list.append(list)

    update = (datetime.datetime.now())            #タイムスタンプ
    print("update",update)
    flg = 0
    del tmp
    del yy
    del list
    del pp
    gc.collect()
update = 0
flg = 0