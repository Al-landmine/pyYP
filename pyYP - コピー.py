#-------------------------------------------------------------------------------
# Name:        main.GUImne
# Purpose:
#
# Author:      Pan
#
# Created:     03/11/2020
# Copyright:   (c) Pan 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import os
import configparser
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkm
import html
import re
import subprocess
import webbrowser
import datetime
import pyperclip
import gc

from tkinter import colorchooser
from tkinter import filedialog
from operator import itemgetter
from playsound import playsound
import conf
import get_ch


#■■■■■■■■■■■■■treeviewのバグ修正用 ■■■■■■■■■■■■■■■
def fixed_map(option):
    # Returns the style map for 'option' with any styles starting with
    # ("!disabled", "!selected", ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
    return [Elm for Elm in style.map("Treeview", query_opt=option)
            if Elm[:2] != ("!disabled", "!selected")]
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

##def get_once():
##    names = get_names()
##    thread = threading.Thread(target=get_ch.get_ch,args = (config,names))
##    thread.daemon = True
##    thread.start()
def get_once():
    names = get_names()
    thread = threading.Thread(target=get_ch.get_ch,args = (config,names))
    thread.daemon = True
    thread.start()

def get_names():
    names =[]
    for n in range(conf.yp_names(config)[1]):
        name = []
        children = ch_list[n].get_children()
        for i in children:
            tmp = ch_list[n].item(i,"values")[2]
            name.append(tmp)
        names.append(name)
    return (names)

def get_start():
    names = get_names()
    thread = threading.Thread(target=get_ch.get_ch,args = (config,names))
    thread.daemon = True
    thread.start()
    try:    #次回更新予約
        if int(config.get("peca","update")) < 1:       #間違ってもF5アタックしないように保険
            after = 60001
        else:
          after = int(config.get("peca","update"))*60000
    except:
        after = 60002
    print("next auto_update",after,"ms")
    root.after(after, get_start)

def show_yp():
# 0 チャンネル名<> 1 ID<> 2 TIP<> 3 コンタクトURL<> 4 ジャンル<> 5 詳細<>
# 6 リスナー数<> 7 リレー数<> 8 ビットレート<> 9 タイプ<> 10 アーティスト<>
# 11 タイトル<> 12 アルバム<> 13 URL2<> 14 チャンネル名（エンコ済み）<>
# 15 配信時間<> 16 ステート<> 17 コメント<> 18 ダイレクト接続
#　後から付加した分
# 19 YP名 20 新着記号 21 フィルタ+背景色 22 すべてタブに表示
# 23 ブラックリスト 24 SEフラグ
    global update2
    all = []
    se = False

    if update2 == get_ch.update_t():
        root.after(1000,show_yp)
        return
    res = get_ch.get_list()
    for n in range(conf.yp_names(config)[1]):
        ch_list[n].delete(*ch_list[n].get_children())   #各YPtabクリア、再現性の無いエラーがたまに出る･･･\
                                                        #YP削除でタイミングが悪いと整合性がとれてない気がする
        ppp = res[n]

        if sort_listener_show.get() == True:
            try:
                ppp.sort(key=itemgetter(6),reverse=True)     #リスナー数順にソート
            except:
                pass
        if sort_filter_show.get() == True:
            try:
                ppp.sort(key=itemgetter(21),reverse=True)    #フィルタソート
            except:
                pass
        for m in range(len(ppp)):
            pppp = ppp[m]
            if pppp[22] == "True":      #全てtabに乗せるか判定1
                all.append(pppp)
            else:
                if conf.get_yp(config,n)[2] == "True":    #全てtabに乗せるか判定2
                    all.append(pppp)
            if m % 2 == 1:              #一行ごとに色を変える
                tag = "g"
            else:
                tag = "w"
            if pppp[21] != "":          #フィルタにかかった物の色を変える
                tag = pppp[21]
                if pppp[20] == "◎" and pppp[23] != "True" and pppp[24] == "True": #ついでに音フラグチェック
                    se = True
            detail =  html.unescape(pppp[4]         #まとめてエスケープコードも変換
                                   +pppp[5]
                                   +pppp[10]
                                   +pppp[11]
                                   +pppp[12]
                                   +pppp[17]
                                   )
            listener = str(pppp[6])+"/"+str(pppp[7])
            ch_list[n] .insert("", "end", values=(pppp[18],
                                                  pppp[20],
                                                  (pppp[0]),
                                                  detail,
                                                  listener,
                                                  pppp[8],
                                                  pppp[15],
                                                  pppp[9],
                                                  pppp[19],
                                                  pppp[3],
                                                  pppp[1],
                                                  pppp[2]
                                                  ),tags = tag)
        #各タブにチャンネル数付加(うーむ後付けで美しくない…）
        try:
            if m % 2 == 1:
                tag = "w"
            else:
                tag = "g"
        except:
            tag = "g"

        ch_list[n] .insert("", "end", values=("0",
                                              "",
                                              (conf.get_yp(config,n)[0]),
                                              "チャンネル数："+str(len(ppp)),
                                              "-99/-99",
                                              "0",
                                              "00:00",
                                              "RAW",
                                              ""
                                              "",
                                              "",
                                              ""
                                              ),tags = tag)
        for c in conf.color_list(config):
            ch_list[n].tag_configure(c,background = c)
        ch_list[n] .tag_configure("g",background='#f0f0f0')

    #全てtab
    #チャンネル数付加
    mess = []
    mess.append("すべて")
    mess.append('')
    mess.append('')
    mess.append('')
    mess.append('')
    mess.append("チャンネル数："+str(len(all)))
    mess.append(-99)
    mess.append("-99")
    mess.append("0")
    mess.append("RAW")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("00:00")
    mess.append("")
    mess.append("")
    mess.append("0")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("")
    mess.append("")
    all.append(mess)
    ch_list_all.delete(*ch_list_all.get_children()) #ch_list_allクリア

    if sort_listener_show.get() == True:
        all.sort(key=itemgetter(6),reverse = True)     #リスナー数順にソート
    if sort_filter_show.get() == True:
        all.sort(key=itemgetter(21),reverse=True)    #フィルタソート

    for m in range(len(all)):

        pppp = all[m]
        if m % 2 == 1:
            tag = "g"
        else:
            tag = "w"
        if pppp[21] == "ch":
            tag = "ch"
        if pppp[21] != "":
            tag = pppp[21]

        detail =  html.unescape( pppp[4]
                                +pppp[5]
                                +pppp[10]
                                +pppp[11]
                                +pppp[12]
                                +pppp[17]
                               )
        listener = str(pppp[6])+"/"+str(pppp[7])

        ch_list_all.insert("", "end", values=(pppp[18],
                                              pppp[20],
                                              (pppp[0]),
                                              detail,
                                              listener,
                                              pppp[8],
                                              pppp[15],
                                              pppp[9],
                                              pppp[19],
                                              pppp[3],
                                              pppp[1],
                                              pppp[2]
                                              ),tags = tag)
    for c in conf.color_list(config):
        ch_list_all.tag_configure(c,background = c)
    ch_list_all.tag_configure("g",background='#f0f0f0')

    if se == True:
        playsound(config.get("set_filter","se"))

    up_time.config(text = "更新:"+(get_ch.update_t().strftime('%H時%M分%S秒　'))
                                 +"更新間隔:"+(config.get("peca","update")+"分"))
    update2 = get_ch.update_t()

    root.after(1000,show_yp)

    del ppp
    del pppp
    del all
    gc.collect()

#終了処理
def on_closing():
    config.set("SETTING","position_x",str(root.winfo_rootx()-4))                #何で補正しないとずれていくのさ？
    config.set("SETTING","position_y",str(root.winfo_rooty()-25))
    config.set("SETTING","window_x",str(root.winfo_width()))
    config.set("SETTING","window_y",str(root.winfo_height()))

    config.set("SETTING","sort_filter",str(sort_filter_show.get()))
    config.set("SETTING","sort_listener",str(sort_listener_show.get()))
    #カラム保存
    aa = ""
    for c in col:
        f = ch_list_all.column(c,"width")  #全てtabのカラムサイズ保存
        if c != "d":
            aa += ","
        aa += str(f)
    config.set("column_size","all",aa)

    for i in range(conf.yp_names(config)[1]):      #各tabの保存
        aa = ""
        ccc = config.get("YP",conf.get_yp(config,i)[0]).split(",")
        for c in col:
            f = ch_list[i].column(c,"width")
            aa = aa + "," + str(f)
        aa =ccc[0]+","+ccc[1]+","+ccc[2]+aa
        config.set("YP",ccc[0],aa)
    conf.save(config)
    root.destroy()

#フィルタ
def set_filter():
    conf.save_tmp(config)  #設定の仮保存

    def handle_click(event): #カラムの変更禁止
        if filt_list.identify_region(event.x, event.y) == "separator":
            return "break"

    def se_path():
        file_path = filedialog.askopenfilename(filetypes = [("", ".wav"),("すべて",".*")],multiple = False)
        m_path.delete(0, tk.END)
        m_path.insert(tk.END,file_path)
        if file_path == "":
            return "break"

    def getcolor():
        colo = colorchooser.askcolor()
        if str(colo[1]) == "None":
            return "break"
        color.config(bg = colo[1])
        color_num.config(state = "normal")
        color_num.delete(0, tk.END)
        color_num.insert(tk.END,str(colo[1]))
        color_num.config(state = "readonly")

    #キャンセルボタン
    def f_exit():
        config = conf.config_tmp()
        filt.destroy()

    #okボタン
    def f_save():
        config.remove_section("filter")
        config.add_section("filter")
        children = filt_list.get_children()
        if len(children) != 0:
            for n in children:
                tmp = filt_list.item(n, 'values')[0:]
                tmp0 = str(tmp[1])  #フィルタ名
                tmp1 = str(tmp[2])  #AND検索1
                tmp2 = str(tmp[3])  #AND検索2
                tmp3 = str(tmp[4])  #NOT検索
                tmp4 = tmp[5]  #bools&色設定+and2+not
                tmpa = tmp1 + "\\\\" + tmp2 + "\\\\" + tmp3 + tmp4
                config.set("filter",tmp0,tmpa)
        config.set("set_filter","se",m_path.get())
        get_ch.search(config,get_names())
        filt.destroy()

    #削除ボタン
    def f_delete():
        delete_item = filt_list.selection()
        if len(delete_item) == 0:
            return
        filt_list.delete(delete_item)

    #フィルタ追加
    def f_add_item():
        if filt_name.get() == "":
            return
        children = filt_list.get_children()
        for n in children:
            tmp = filt_list.item(n, 'values')[1]
            if tmp == filt_name.get():
                tkm.showinfo(title="エラー", message="同じ名前は作れません。")
                return
        tmp = ""
        for n in range(3):
            tmp += "\\\\" + str(chname_show[n].get())
            tmp += "\\\\" + str(genre_show[n].get())
            tmp += "\\\\" + str(details_show[n].get())
            tmp += "\\\\" + str(comment_show[n].get())
            tmp += "\\\\" + str(artist_show[n].get())
            tmp += "\\\\" + str(title_show[n].get())
            tmp += "\\\\" + str(album_show[n].get())
            tmp += "\\\\" + str(ypname_show[n].get())
            tmp += "\\\\" + str(conturl_show[n].get())
            tmp += "\\\\" + str(type_show[n].get())
        tmp += "\\\\" + str(alltab_show.get())
        tmp += "\\\\" + str(sound_show.get())
        tmp += "\\\\" + str(bl_show.get())
        tmp += "\\\\" + color_num.get()
        tmp += "\\\\" + str(on_show.get())
        tmp += "\\\\" + str(and2_show.get())
        tmp += "\\\\" + str(not2_show.get())
        if on_show.get() == "1":
            mark = "○"
        else:
            mark = "×"    #
        filt_list.insert("","end",values = (mark,filt_name.get(),
                                            str(entry[0].get()),
                                            str(entry[1].get()),
                                            str(entry[2].get()),
                                            tmp),
                                            tags = color_num.get())
        filt_list.tag_configure(color_num.get(),background = color_num.get())
        root.after(100,lambda : filt_list.yview_moveto(1)) #ウェイト入れないと一番下にスクロールしない
        filt_list.selection_remove(filt_list.selection()) #選択解除

    #上書きボタン
    def f_edit():
        if filt_name.get() == "":
            return
        if len(filt_list.selection()) == 0:
            tkm.showinfo(title="エラー", message="アイテムが選択されていません。")
            return
        else:
            children = filt_list.get_children()
            for n in children:
                tmp = filt_list.item(n, 'values')[0]
                if tmp == filt_name.get():
                    if n == filt_list.selection()[0]:
                        break
                    tkm.showinfo(title="エラー", message="同じ名前は作れません。")
                    return
            tmp = ""
            for n in range(3):
                tmp += "\\\\" + str(chname_show[n].get())
                tmp += "\\\\" + str(genre_show[n].get())
                tmp += "\\\\" + str(details_show[n].get())
                tmp += "\\\\" + str(comment_show[n].get())
                tmp += "\\\\" + str(artist_show[n].get())
                tmp += "\\\\" + str(title_show[n].get())
                tmp += "\\\\" + str(album_show[n].get())
                tmp += "\\\\" + str(ypname_show[n].get())
                tmp += "\\\\" + str(conturl_show[n].get())
                tmp += "\\\\" + str(type_show[n].get())
            tmp += "\\\\" + str(alltab_show.get())
            tmp += "\\\\" + str(sound_show.get())
            tmp += "\\\\" + str(bl_show.get())
            tmp += "\\\\" + color_num.get()
            tmp += "\\\\" + str(on_show.get())
            tmp += "\\\\" + str(and2_show.get())
            tmp += "\\\\" + str(not2_show.get())
            if on_show.get() == "1":
                mark = "○"
            else:
                mark = "×"    #
            filt_list.item(filt_list.selection(),values = (mark,filt_name.get(),
                                                           str(entry[0].get()),
                                                           str(entry[1].get()),
                                                           str(entry[2].get()),
                                                           tmp),
                                                           tags = color_num.get())
            filt_list.tag_configure(color_num.get(),background = color_num.get())
        filt_list.selection_remove(filt_list.selection())  #選択解除

    #アップダウン
    def f_up():
        try:
            my = (filt_list.selection())
            ff = filt_list.index(my)
            filt_list.move(my,"",ff-1)
        except:
            return ()

    def f_down():
        try:
            my = (filt_list.selection())
            ff = filt_list.index(my)
            filt_list.move(my,"",ff+1)
        except:
            return ()

    #フィルタをクリックした時
    def f_set_click(event):
        if len(filt_list.selection()) == 0:
            return
        for item in filt_list.selection():
            m=(item, filt_list.item(item))

        filt_name.delete(0, tk.END)
        filt_name.insert(tk.END,m[1]['values'][1])
        entry[0].delete(0, tk.END)
        entry[0].insert(tk.END,m[1]['values'][2])
        entry[1].delete(0, tk.END)
        entry[1].insert(tk.END,m[1]['values'][3])
        entry[2].delete(0, tk.END)
        entry[2].insert(tk.END,m[1]['values'][4])

        mm = str((m[1]['values'][5]))
        mm = mm.split("\\\\")
        num = 1


        for b in range(3):
            chname_show[b].set(mm[num])
            num += 1
            genre_show[b].set(mm[num])
            num += 1
            details_show[b].set(mm[num])
            num += 1
            comment_show[b].set(mm[num])
            num += 1
            artist_show[b].set(mm[num])
            num += 1
            title_show[b].set(mm[num])
            num += 1
            album_show[b].set(mm[num])
            num += 1
            ypname_show[b].set(mm[num])
            num += 1
            conturl_show[b].set(mm[num])
            num += 1
            type_show[b].set(mm[num])
            num += 1
        alltab_show.set(mm[num])
        num += 1
        sound_show.set(mm[num])
        num += 1
        bl_show.set(mm[num])
        num += 1
        color_num.config(state = "normal")
        color_num.delete(0, tk.END)
        color_num.insert(tk.END,mm[num])
        color_num.config(state = "readonly")
        color.config(bg = mm[num])
        num += 1
        on_show.set(mm[num])
        num += 1
        and2_show.set(mm[num])
        num += 1
        not2_show.set(mm[num])

    #フィルタウィンドウ
    filt = tk.Toplevel(root)
    filt.title("フィルタ")
    x = root.winfo_rootx() - 100
    if x < 0:
        x = 0
    y = root.winfo_rooty() - 100
    if y < 0:
        y = 0
    position = "530x500" + "+" + str(x) + "+" + str(y)
    filt.geometry(position)
    filt.resizable(0,0)
    filt.grab_set()

    #リストフレーム
    filt_flame = tk.Frame(filt,height = 200,background="#ffffff")
    filt_flame.pack(expand= 0 , fill = 'x',side = "top",anchor ="n")

    column_f = ["switch","name","and1","and2","not","bools"]
    filt_list = ttk.Treeview(filt_flame, columns = column_f, show="headings",selectmode = "browse")

    scrollbary = ttk.Scrollbar(filt_flame, orient=tk.VERTICAL,command=filt_list.yview)
    scrollbary.pack(fill = "y", side = "right")
    filt_list.pack(fill = "both",)

    filt_list.column("switch" , width =  20,anchor=tk.W,stretch = "False")
    filt_list.column("name"   , width =  90,anchor=tk.W,stretch = "False")
    filt_list.column("and1"   , width = 220,anchor=tk.W,stretch = "False")
    filt_list.column("and2"   , width = 90,anchor=tk.W,stretch = "False")
    filt_list.column("not"    , width = 90,anchor=tk.W,stretch = "False")
    filt_list.column("bools"  , width = 0)

    filt_list.heading("switch" , text = "on")
    filt_list.heading("name"   , text = "名前")
    filt_list.heading("and1"   , text = "AND1")
    filt_list.heading("and2"   , text = "AND2")
    filt_list.heading("not"    , text = "NOT")
    filt_list.heading("bools"  , text = "bools")

    filt_list.pack(side = tk.LEFT,expand=0, fill='both')

    filt_list.config(yscrollcommand=scrollbary.set)

    filt_list.bind('<Button-1>', handle_click)
    filt_list.bind("<<TreeviewSelect>>", f_set_click)

    #フィルターリストに表示

    for n in config.options("filter"):
        p = config.get("filter",n).split("\\\\")
        tmp = ""
        for i in range(3,40):
            tmp += "\\\\" + str(p[i])
        if p[37] == "1":
            mark = "○"
        else:
            mark = "×"     #####
        tag = p[36]
        filt_list.insert("","end",values = (mark,n,p[0],p[1],p[2],tmp),tags = p[36])
    for c in conf.color_list(config):
        filt_list.tag_configure(c,background = c)


    #フィルタ名
    filt_name_l = tk.Label(filt,text = "名前",font = ("",10))
    filt_name = tk.Entry (filt,width = 15,font = ("",11))
    filt_name_l.pack(expand= 0 ,side = "left",anchor ="n",pady = 5,padx = 5)
    filt_name.pack(expand= 0 ,side = "left",anchor ="n",pady = 5,padx = 5,ipadx = 5)

    add_button    = tk.Button(filt,
                              text    = "追加",
                              width   = "6",
                              height  = "1",
                              font    = ("",10),
                              command = lambda : f_add_item())

    del_button    = tk.Button(filt,
                              text    = "削除",
                              width   = "6",
                              height  = "1",
                              font    = ("",10),
                              command = lambda : f_delete())

    edit_button    = tk.Button(filt,
                              text    = "上書き",
                              width   = "6",
                              height  = "1",
                              font    = ("",10),
                              command = lambda : f_edit())

    f_up_button     = tk.Button(filt,text = "∧",width = 5,font = ("",10),command = lambda : f_up())
    f_down_button   = tk.Button(filt,text = "∨",width = 5,font = ("",10),command = lambda : f_down())


    ok_button     = tk.Button(filt,text = "OK",width = 10,font = ("",10),command = lambda : f_save())
    cancel_button = tk.Button(filt,text = "キャンセル",width =10,font = ("",10),command = lambda : f_exit())

    add_button.pack   (expand= 0 ,side = "left" ,anchor ="nw",padx = 5,pady = 5)
    edit_button.pack  (expand= 0 ,side = "left" ,anchor ="nw",padx = 5,pady = 5)
    del_button.pack   (expand= 0 ,side = "left" ,anchor ="nw",padx = 5,pady = 5)
    f_down_button.pack(expand= 0 ,side = "right",anchor ="ne",padx =20,pady = 5)
    f_up_button.pack  (expand= 0 ,side = "right",anchor ="ne",padx = 0,pady = 5)

    ok_button.place(x = 340 , y = 470)
    cancel_button.place(x = 430 , y = 470)


    m_path_label = tk.Label (filt,text  = "se.パス",font = ("",10))
    m_path = tk.Entry (filt,width = 54,font = ("",11))
    m_pathb = tk.Button(filt,
                        text    = "♪",
                        width   = "6",
                        height  = "1",
                        font    = ("",10),
                        command = lambda : se_path())

    m_path.insert(tk.END,config.get("set_filter","se"))

    m_path_label.place(x =  5 , y = 380)
    m_path.place(x =  12 , y = 405)
    m_pathb.place (x = 458 ,y = 402)

    #フィルタセッティングフレーム
    filt_set_f = tk.Frame(filt,height = 160,width = 490)
    filt_set_f.place(x = 5 ,y = 258)

    filt_set = []
    tab      = []
    chname   = []
    genre    = []
    details  = []
    comment  = []
    artist   = []
    title    = []
    album    = []
    ypname   = []
    conturl  = []
    type     = []

    chname_show  = []
    genre_show   = []
    details_show = []
    comment_show = []
    artist_show  = []
    title_show   = []
    album_show   = []
    ypname_show  = []
    conturl_show = []
    type_show    = []

    entry = []

    tb2 = ttk.Notebook(filt_set_f,height = 90,width = 515)
    tb2.grid()

    tab_list = ["AND1","AND2","NOT","オプション"]

    #設定タブ
    for n in range(len(tab_list)):
        tab.append(n)
        filt_set.append(n)
        tab[n] = tk.Frame(tb2)
        tb2.add(tab[n], text = str(tab_list[n]).ljust(10))
        filt_set[n] = ttk.Treeview(tab[n], show="headings",selectmode = "browse")
        if n == 3:
            break

        chname.append(n)
        genre.append(n)
        details.append(n)
        comment.append(n)
        artist.append(n)
        title.append(n)
        album.append(n)
        ypname.append(n)
        conturl.append(n)
        type.append(n)

        chname_show.append(n)
        genre_show.append(n)
        details_show.append(n)
        comment_show.append(n)
        artist_show.append(n)
        title_show.append(n)
        album_show.append(n)
        ypname_show.append(n)
        conturl_show.append(n)
        type_show.append(n)

        chname_show[n]  = tk.StringVar()
        genre_show[n]   = tk.StringVar()
        details_show[n] = tk.StringVar()
        comment_show[n] = tk.StringVar()
        artist_show[n]  = tk.StringVar()
        title_show[n]   = tk.StringVar()
        album_show[n]   = tk.StringVar()
        ypname_show[n]  = tk.StringVar()
        conturl_show[n] = tk.StringVar()
        type_show[n]    = tk.StringVar()

        chname_show[n].set("0")
        genre_show[n].set("0")
        details_show[n].set("0")
        comment_show[n].set("0")
        artist_show[n].set("0")
        title_show[n].set("0")
        album_show[n].set("0")
        ypname_show[n].set("0")
        conturl_show[n].set("0")
        type_show[n].set("0")

        chname[n]  = tk.Checkbutton(tab[n],variable = chname_show[n] ,text = "チャンネル名" ,font = ("",10),height = 1)
        genre[n]   = tk.Checkbutton(tab[n],variable = genre_show[n]  ,text = "ジャンル"     ,font = ("",10),height = 1)
        details[n] = tk.Checkbutton(tab[n],variable = details_show[n],text = "詳細"         ,font = ("",10),height = 1)
        comment[n] = tk.Checkbutton(tab[n],variable = comment_show[n],text = "コメント"     ,font = ("",10),height = 1)
        artist[n]  = tk.Checkbutton(tab[n],variable = artist_show[n] ,text = "アーティスト" ,font = ("",10),height = 1)
        title[n]   = tk.Checkbutton(tab[n],variable = title_show[n]  ,text = "タイトル"     ,font = ("",10),height = 1)
        album[n]   = tk.Checkbutton(tab[n],variable = album_show[n]  ,text = "アルバム"     ,font = ("",10),height = 1)
        ypname[n]  = tk.Checkbutton(tab[n],variable = ypname_show[n] ,text = "YP名"         ,font = ("",10),height = 1)
        conturl[n] = tk.Checkbutton(tab[n],variable = conturl_show[n],text = "コンタクトURL",font = ("",10),height = 1)
        type[n]    = tk.Checkbutton(tab[n],variable = type_show[n]   ,text = "タイプ"       ,font = ("",10),height = 1)

        entry.append(n)
        entry[n] = tk.Entry (tab[n],width = 48 ,font = ("",11))

        chname[n].grid(column  = 0, row = 0,padx = 5,pady = 5,sticky = "w")
        genre[n].grid(column   = 1, row = 0,padx = 5,pady = 5,sticky = "w")
        details[n].grid(column = 2, row = 0,padx = 5,pady = 5,sticky = "w")
        comment[n].grid(column = 3, row = 0,padx = 5,pady = 5,sticky = "w")
        artist[n].grid(column  = 4, row = 0,padx = 5,pady = 5,sticky = "w")
        title[n].grid(column   = 0, row = 1,padx = 5,pady = 5,sticky = "w")
        album[n].grid(column   = 1, row = 1,padx = 5,pady = 5,sticky = "w")
        ypname[n].grid(column  = 2, row = 1,padx = 5,pady = 5,sticky = "w")
        conturl[n].grid(column = 3, row = 1,padx = 5,pady = 5,sticky = "w")
        type[n].grid(column    = 4, row = 1,padx = 5,pady = 5,sticky = "w")
        entry[n].grid(column   = 0, row = 2, columnspan = 5,sticky = "e",padx = 5)

    on_show   = tk.StringVar()
    and2_show = tk.StringVar()
    not2_show = tk.StringVar()
    on_show.set("1")
    and2_show.set("0")
    not2_show.set("0")

    and1 = tk.Checkbutton(tab[0],variable = on_show ,text   = "on/off"  ,font = ("",10),height = 1)
    and2 = tk.Checkbutton(tab[1],variable = and2_show ,text = "AND検索" ,font = ("",10),height = 1)
    not2 = tk.Checkbutton(tab[2],variable = not2_show ,text = "NOT検索" ,font = ("",10),height = 1)

    and1.place(x = 5, y = 63)
    and2.place(x = 5, y = 63)
    not2.place(x = 5, y = 63)

    alltab_show = tk.StringVar()
    sound_show  = tk.StringVar()
    bl_show     = tk.StringVar()
    alltab_show.set("1")
    sound_show.set("0")
    bl_show.set("0")

    alltab = tk.Checkbutton(tab[3],variable = alltab_show,text = "すべてタブに表示する",font = ("",10),height = 1)
    sound = tk.Checkbutton(tab[3],variable = sound_show,text = "新着時音を鳴らす",font = ("",10),height = 1)
    bl = tk.Checkbutton(tab[3],variable = bl_show,text = "ブラックリスト(非表示)",font = ("",10),height = 1)
    default = "#ffffff"
    color = tk.Button(tab[3],text="背景色", command = getcolor,bg = default,font=("",9))
    color_num = tk.Entry (tab[3],width = 16,font = ("",11))
    color_num.config(state = "normal")
    color_num.delete(0, tk.END)
    color_num.insert(tk.END,default)
    color_num.config(state = "readonly")

    alltab.grid   (column = 0, row = 0,padx = 5,pady = 5,sticky = "w")
    sound.grid    (column = 0, row = 1,padx = 5,pady = 5,sticky = "w")
    bl.grid       (column = 0, row = 2,padx = 5,pady = 5,sticky = "w")
    color.grid    (column = 1, row = 0,padx = 5,pady = 5,sticky = "w")
    color_num.grid(column = 2, row = 0,padx = 5,pady = 5,sticky = "w")
#設定
def settings():
    conf.save_tmp(config)

    #YP設定をクリックした時 (ツリーアイテム取得テンプレ)
    def set_click(event):
        if len(yp.selection()) == 0:
            return
        for item in yp.selection():
            m=(item, yp.item(item))
        add_ypname.delete(0, tk.END)
        add_ypname.insert(tk.END,m[1]['values'][0])
        add_url.delete(0, tk.END)
        add_url.insert(tk.END,m[1]['values'][1])
        if (m[1]['values'][2])== "True":
            show.set(True)
        else:
            show.set(False)

    #okボタン
    def ok():
        config.remove_section("YP")
        config.add_section("YP")
        for n in yp.get_children():
            yp_tree = ""
            tmp = yp.item(n, 'values')[0:]
            tmp0 = str(tmp[0])  #YP名
            tmp1 = str(tmp[1])  #コンタクトURL
            tmp2 = str(tmp[2])  #全てタブに表示
            tmp3 = str(tmp[3])
            yp_tree = tmp0 + "," + tmp1 + "," + tmp2 + "," + tmp3
            config.set("YP",tmp0,yp_tree)
        #peca_port
        config.set("peca","peca_port",peercast_port.get())
        config.set("peca","peca_port2",peercast2_port.get())

        #更新間隔
        config.set("peca","update",str(a_update.get()))

        #タイムアウト
        config.set("peca","timeout",str(timeout.get()))

        yp_tab.destroy()
        new_tab()
        get_once()
        set.destroy()

    #キャンセルボタン
    def exit():
        config = conf.config_tmp()
        set.destroy()

    #追加ボタン
    def add_item():
        if add_ypname.get() == "" or add_url.get() == "":
            return
        else:
            for n in yp.get_children():
                if str(yp.item(n)['values'][0]).lower() == add_ypname.get().lower():
                    tkm.showinfo(title="エラー", message="同じYP名は作れません。")
                    return
            yp.insert("","end",values = (add_ypname.get(),
                                         add_url.get(),
                                         show.get(),
                                         config.get("column_size","all")))
            root.after(100,lambda : yp.yview_moveto(1))    #遅らせないとスクロールバーが反映しない
            yp.selection_remove(yp.selection())  #選択解除

    #YP削除
    def delete():
        delete_item = yp.selection()
        if len(delete_item) == 0:
            return
        yp.delete(delete_item)

    #上書きボタン
    def edit():
        if add_ypname.get() == "" or add_url.get() == "":
            return
        if len(yp.selection()) == 0:
            return
        else:
            c = yp.item(yp.selection())['values'][3]
            yp.item(yp.selection(),values =(add_ypname.get(),
                                            add_url.get(),
                                            show.get(),c))
        yp.selection_remove(yp.selection())  #選択解除

    #ソート
    def s_up():
        try:
            sort = (yp.selection())
            n = yp.index(sort)
            yp.move(sort,"",n-1)
        except:
            return ()

    def s_down():
        try:
            sort = (yp.selection())
            n = yp.index(sort)
            yp.move(sort,"",n+1)
        except:
            return ()

    #設定ウィンドウ
    set = tk.Toplevel(root)
    set.title("設定")
    x = root.winfo_rootx() - 100
    if x < 0:
        x = 0
    y = root.winfo_rooty() - 100
    if y < 0:
        y = 0
    position = "400x505" + "+" + str(x) + "+" + str(y)
    set.geometry(position)
    set.resizable(0,0)
    set.grab_set()

    #設定tab作成
    param=["YP","Player","tool"]
    tab_set=[]
    set_window = ttk.Notebook(set)
    for n in range(len(param)):
        tab_set.append(n)
        tab_set[n] = tk.Frame(set,height = 500,relief = "flat")
        set_window.add(tab_set[n], text = param[n].center(10))
        set_window.pack(side = "top",fill = 'both',padx = 2,pady = 2)

    #YP設定
    def handle_click_yp(event):     #カラムサイズ変更禁止
        if yp.identify_region(event.x, event.y) == "separator":
            return "break"

    list_frame = tk.Frame(tab_set[0],relief = "flat")
    list_frame.pack(side = "top" ,fill = "x",padx = 3,pady = 3)

    yp = ttk.Treeview(list_frame,
                      columns    = ("ypname","URL","all","column"),
                      show       = "headings",
                      selectmode = "browse",
                      height     = 9)

    yp.bind('<Button-1>', handle_click_yp)

    scrollbar_sety = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,command=yp.yview)
    scrollbar_sety.pack(side = "right",fill = "y")

    yp.config(yscrollcommand=scrollbar_sety.set)
    yp.column("ypname",width =  75,minwidth =  75,stretch = "False")
    yp.column("URL",   width = 200,minwidth = 200,stretch = "False")
    yp.column("all",   width = 100,minwidth = 100,stretch = "False",anchor=tk.CENTER)
    yp.heading("ypname", text = "YP名")
    yp.heading("URL", text = "URL")
    yp.heading("all", text = "すべてに表示")
    yp.pack(side = "left",fil = "x")

    for n in range(conf.yp_names(config)[1]):
        b = conf.get_yp(config,n)
        bb = ""
        for nn in range(3,14):
            if nn != 3:
                bb += ","
            bb += b[nn]
        yp.insert("","end",values = (b[0],b[1],b[2],bb))

    #各ボタンフレーム
    button_frame = tk.Frame(tab_set[0],
                            height = 95,
                            width = 100,
                            relief = "flat",
                            bd = 3,
                            bg = "#aad2ff")

    button_frame.pack(side = "top" ,fill = "x",padx = 3,pady = 3)

    add_button = tk.Button(button_frame,
                           text    = "追加",
                           width   = "6",
                           height  = "1",
                           font    = ("",10),
                           command = lambda : add_item())

    edit_button = tk.Button(button_frame,
                           text    = "上書き",
                           width   = "6",
                           height  = "1",
                           font    = ("",10),
                           command = lambda : edit())

    del_button = tk.Button(button_frame,
                           text    = "削除",
                           width   = "6",
                           height  = "1",
                           font    = ("",10),
                           command = lambda : delete())

    up_button = tk.Button(button_frame,
                          text  = "∧",
                          width = 5,
                          font = ("",10),
                          command = lambda : s_up())

    down_button = tk.Button(button_frame,
                            text  = "∨",
                            width = 5,
                            font = ("",10),
                            command = lambda : s_down())

    add_label  = tk.Label (button_frame,text  = "YP名",font=("",10),bg = "#aad2ff")
    add_ypname = tk.Entry (button_frame,width = 20,font = ("",11))

    url_label  = tk.Label (button_frame,text  = "URL",font = ("",10),bg = "#aad2ff")
    add_url    = tk.Entry (button_frame,width = 46,font = ("",10))

    show = tk.BooleanVar()
    show.set(True)
    all_check = tk.Checkbutton(button_frame,
                                   text  = "すべてタブに表示する",
                                   variable = show,
                                   font = ("",10),
                                   bg = "#aad2ff")

    peercast_label= tk.Label (tab_set[0],text  = "PeerCast",font = ("",10))
    peercast_port = tk.Entry (tab_set[0],width = 25,font = ("",10))
    peercast_port.insert(0, config.get("peca","peca_port"))
    peercast_labe2= tk.Label (tab_set[0],text = "Host:Port / IP:Port",font = ("",11))

    peercast2_label= tk.Label (tab_set[0],text  = "PeerCast2",font = ("",10))
    peercast2_port = tk.Entry (tab_set[0],width = 25,font = ("",10))
    peercast2_port.insert(0, config.get("peca","peca_port2"))
    peercast2_labe2= tk.Label (tab_set[0],text = "Host:Port / IP:Port",font = ("",11))

    var = tk.IntVar(master = tab_set[0],value = config.get("peca","update"))
    a_update = tk.Scale(tab_set[0],
                        from_=1,to=15,
                        label = "自動更新間隔：分",
                        length = 110,
                        font = ("",10),
                        orient = tk.HORIZONTAL,
                        variable = var)

    var2 = tk.IntVar(master = tab_set[0],value = config.get("peca","timeout"))
    timeout = tk.Scale(tab_set[0],
                       from_=5,to=60,
                       label = "タイムアウト：秒",
                       length = 250,
                       font = ("",10),
                       orient = tk.HORIZONTAL,
                       variable = var2)

    ok_button     = tk.Button(tab_set[0],
                              text  = "OK",
                              width = 10,
                              font = ("",10),
                              command = lambda:ok())

    cancel_button = tk.Button(tab_set[0],
                              text  = "キャンセル",
                              width =10,
                              font = ("",10),
                              command = lambda:exit())


    add_button.place  (x = 10, y =  5)
    edit_button.place (x = 75, y =  5)
    del_button.place  (x =140, y =  5)
    add_label.place   (x =  7, y = 35)
    add_ypname.place  (x = 45, y = 35)
    url_label.place   (x =  7, y = 65)
    add_url.place     (x = 45, y = 65)
    all_check.place   (x =230, y = 35)
    up_button.place   (x =270, y =  5)
    down_button.place (x =327, y =  5)

    peercast_label.place (x =  2, y = 315)
    peercast_port.place  (x = 70, y = 315)
    peercast_labe2.place (x =255, y = 312)
    peercast2_label.place(x =  2, y = 345)
    peercast2_port.place (x = 70, y = 345)
    peercast2_labe2.place(x =255, y = 342)

    a_update.place (x = 10, y = 370)
    timeout.place  (x =130, y = 370)

    cancel_button.pack (side = "right",anchor = "s",padx = 5)
    ok_button.pack     (side = "right",anchor = "s",padx = 5)

    yp.bind("<<TreeviewSelect>>", set_click)


#設定Player
    def handle_click_yp(event):     #カラムサイズ変更禁止
        if player.identify_region(event.x, event.y) == "separator":
            return "break"

    def p_ok():
        num = 1
        config.remove_section("player")
        config.add_section("player")
        for n in player.get_children():
            player_tree =""
            tmp = player.item(n, 'values')[0:]
            tmp1 = str(tmp[0])  #player path
            tmp2 = str(tmp[1])  #augment
            tmp3 = str(tmp[2])  #type
            player_tree = tmp1 + "," +tmp2 + "," + tmp3
            config.set("player",str(num),player_tree)
            num += 1
        set.destroy()

    #playerの追加
    def p_add_item():
        if p_path.get() == "" or p_arg.get() == "" or p_type.get() == "":
            return
        player.insert("","end",values = (p_path.get(),p_arg.get(),p_type.get()))
        root.after(100,lambda : player.yview_moveto(1))
        player.selection_remove(player.selection())  #選択解除

    #Player削除
    def p_delete():
        delete_item = player.selection()
        if len(delete_item) == 0:
            return
        player.delete(delete_item)

    #上書きボタン
    def p_edit():
        if len(player.selection()) == 0:
            return
        else:
            f = player.selection()#['values'][3]
            player.item(player.selection(),values = (p_path.get(),
                                                     p_arg.get(),
                                                     p_type.get()))
        player.selection_remove(player.selection())  #選択解除

    #ソート
    def p_up():
        try:
            sort = (player.selection())
            n = player.index(sort)
            player.move(sort,"",n-1)
        except:
            return ()

    def p_down():
        try:
            sort = (player.selection())
            n = player.index(sort)
            player.move(sort,"",n+1)
        except:
            return ()

    #playertreeをクリックした時
    def p_set_click(event):
        if len(player.selection()) == 0:
            return
        for item in player.selection():
            m=(item, player.item(item))
        p_path.delete(0, tk.END)
        p_path.insert(tk.END,m[1]['values'][0])
        p_arg.delete(0, tk.END)
        p_arg.insert(tk.END,m[1]['values'][1])
        p_type.delete(0, tk.END)
        p_type.insert(tk.END,m[1]['values'][2])

    #path選択
    def path():
        file_path = filedialog.askopenfilename(filetypes = [("", ".exe"),("すべて",".*")],multiple = False)
        p_path.delete(0, tk.END)
        p_path.insert(tk.END,file_path)
        if file_path == "":
            return "break"

    #GUI
    player = ttk.Treeview(tab_set[1],
                      columns    = ("player","argument","type"),
                      show       = "headings",
                      selectmode = "browse",
                      height     = 7)

    p_scrollbar_sety = ttk.Scrollbar(tab_set[1], orient=tk.VERTICAL,command=player.yview)
    p_scrollbar_sety.grid(row = 0,column = 1,sticky = "ens")

    player.config(yscrollcommand=p_scrollbar_sety.set)
    player.column("player",width = 200,minwidth = 200,stretch = "False")
    player.column("argument", width = 100,minwidth = 100,stretch = "False")
    player.column("type", width = 70,minwidth = 70,stretch = "False",anchor=tk.CENTER)
    player.heading("player", text = "プレイヤーのファイルパス")
    player.heading("argument", text = "引数")
    player.heading("type", text = "タイプ")
    player.grid(row = 0,column =0,sticky = "nsw")

    p_frame = tk.Frame(tab_set[1],relief = "flat",height = 240,bg = "#aad2ff")
    p_frame.grid(row = 1, column = 0,columnspan = 3,padx = 3, pady = 5,sticky = "ew")

    player.bind('<Button-1>', handle_click_yp)

    #treeにplayerの表示
    for n in config.options("player"):
        p = config.get("player",n).split(",")
        player.insert("","end",values = (p[0],p[1],p[2]))

    p_add_button = tk.Button(p_frame,
                             text    = "追加",
                             width   = "6",
                             height  = "1",
                             font    = ("",10),
                             command = lambda : p_add_item())

    p_edit_button = tk.Button(p_frame,
                              text    = "上書き",
                              width   = "6",
                              height  = "1",
                              font    = ("",10),
                              command = lambda : p_edit())

    p_del_button = tk.Button(p_frame,
                             text    = "削除",
                             width   = "6",
                             height  = "1",
                             font    = ("",10),
                             command = lambda : p_delete())

    p_up_button   = tk.Button(p_frame,text  = "∧",width = 5,font = ("",10),command = lambda : p_up())
    p_down_button = tk.Button(p_frame,text  = "∨",width = 5,font = ("",10),command = lambda : p_down())

    p_path = tk.Entry (p_frame,width = 43,font = ("",10))
    p_pathb = tk.Button(p_frame,
                        text    = "選択",
                        width   = "6",
                        height  = "1",
                        font    = ("",10),
                        command = lambda : path())

    p_arg_label = tk.Label (p_frame,text  = "引数",font=("",10),bg = "#aad2ff")
    p_arg = tk.Entry (p_frame,width = 30,font = ("",10))

    p_type_label = tk.Label (p_frame,text  = "タイプ",font=("",10),bg = "#aad2ff")
    p_type = tk.Entry (p_frame,width = 30,font = ("",10))

    p2_frame = tk.LabelFrame(p_frame,width = 372,height = 110,text = "引数",bg = "#aad2ff")
    p_frame_label = tk.Label (p2_frame,
                              text  = "$0=チャンネル名    $1=ID    $2=TIP    $3=コンタクトURL\n"
                                    + "$9=Type    $$=$\n"
                                    + "$X=プレイリストURL(http://Host:port/pls/ID?tip=TIP)\n"
                                    + "$x=プレイリストURL(http://IP:port/pls/ID?tip=TIP)\n"
                                    + "$Y=ストリームURL(http://Host:port/stream/ID.Type)\n"
                                    + "$y=ストリームURL(http://IP:port/stream/ID.Type)",
                              justify = "left",
                              font=("",10),
                              bg = "#aad2ff")

    pp_frame = tk.Frame(tab_set[1],relief = "flat",height = 50)
    pp_frame.grid(row = 2, column = 0,columnspan = 3, sticky = "nsew")

    p_ok_button = tk.Button(pp_frame,text = "OK",
                            width = 10,
                            font = ("",10),
                            command = lambda : p_ok())

    p_cancel_button = tk.Button(pp_frame,text = "キャンセル",
                                width =10,
                                font = ("",10),
                                command = lambda : exit())


    p_add_button.place (x =  5, y =  8)
    p_edit_button.place(x = 70, y =  8)
    p_del_button.place (x =135, y =  8)
    p_up_button.place  (x =270, y =  8)
    p_down_button.place(x =327, y =  8)

    p_path.place       (x =  5, y =  40)
    p_pathb.place      (x =320, y =  37)
    p_arg_label.place  (x =  7, y =  70)
    p_arg.place        (x = 50, y =  70)
    p_type_label.place (x =  5, y = 100)
    p_type.place       (x = 50, y = 100)
    p2_frame.place     (x =  5, y = 125)
    p_frame_label.place(x =  0, y =   0)

    p_ok_button.place     (x =217, y = 27)
    p_cancel_button.place (x =307, y = 27)

    player.bind("<<TreeviewSelect>>", p_set_click)

#tool
    def handle_click_yp(event):     #カラムサイズ変更禁止
        if tool.identify_region(event.x, event.y) == "separator":
            return "break"

    def t_ok():
        config.remove_section("tool")
        config.add_section("tool")
        for n in tool.get_children():
            tool_tree =""
            tmp = tool.item(n, 'values')[0:]
            tool_tree = tmp[1] + "," +tmp[2]
            config.set("tool",tmp[0],tool_tree)
        menu_3.delete(0, 'end')
        menu_3_s.delete(0, 'end')
        for n in config.options("tool"):
            menu_3.add_command(label = n.ljust(20),command = lambda arg=n: tools(arg))
        for n in config.options("tool"):
            menu_3_s.add_command(label = n.ljust(20),command = lambda arg=n: tools(arg))
        set.destroy()

    #toolの追加
    def t_add_item():
        if t_add_name.get() == "":
            return
        else:
            for n in tool.get_children():
                if str(tool.item(n)['values'][0]).lower() == t_add_name.get().lower():
                    tkm.showinfo(title="エラー", message="同じYP名は作れません。")
                    return
            tool.insert("","end",values = (t_add_name.get(),t_path.get(),t_arg.get()))
            root.after(100,lambda : tool.yview_moveto(1))
            tool.selection_remove(tool.selection())  #選択解除

    #tool削除
    def t_delete():
        delete_item = tool.selection()
        if len(delete_item) == 0:
            return
        tool.delete(delete_item)

    #上書きボタン
    def t_edit():
        if t_add_name.get() == "":
            return
        if len(tool.selection()) == 0:
            return
        else:
            f = tool.selection()
            tool.item(tool.selection(),values = (t_add_name.get(),
                                                 t_path.get(),
                                                 t_arg.get()))
        tool.selection_remove(tool.selection())  #選択解除
    #ソート
    def t_up():
        try:
            sort = (tool.selection())
            n = tool.index(sort)
            tool.move(sort,"",n-1)
        except:
            return ()

    def t_down():
        try:
            sort = (tool.selection())
            n = tool.index(sort)
            tool.move(sort,"",n+1)
        except:
            return ()

    #tooltreeをクリックした時
    def t_set_click(event):
        if len(tool.selection()) == 0:
            return
        for item in tool.selection():
            m=(item, tool.item(item))
        t_add_name.delete(0, tk.END)
        t_add_name.insert (tk.END,m[1]['values'][0])
        t_path.delete    (0, tk.END)
        t_path.insert     (tk.END,m[1]['values'][1])
        t_arg.delete     (0, tk.END)
        t_arg.insert      (tk.END,m[1]['values'][2])


    #path選択
    def tool_path():
        file_path = filedialog.askopenfilename(filetypes = [("", ".exe"),("すべて",".*")],multiple = False)
        t_path.delete(0, tk.END)
        t_path.insert(tk.END,file_path)
        if file_path == "":
            return "break"
    #GUI
    tool = ttk.Treeview(tab_set[2],
                      columns    = ("name","tool","argument"),
                      show       = "headings",
                      selectmode = "browse",
                      height     = 7)

    t_scrollbar_sety = ttk.Scrollbar(tab_set[2], orient = tk.VERTICAL,command = tool.yview)
    t_scrollbar_sety.grid(row = 0,column = 1,sticky = "ens")

    tool.config(yscrollcommand=t_scrollbar_sety.set)
    tool.column("name",width = 70,minwidth = 70,stretch = "False")
    tool.column("tool",width = 200,minwidth = 200,stretch = "False")
    tool.column("argument", width = 100,minwidth = 100,stretch = "False")

    tool.heading("name", text = "名前")
    tool.heading("tool", text = "ツールのパス")
    tool.heading("argument", text = "引数")
    tool.grid(row = 0,column =0,sticky = "nsw")

    t_frame = tk.Frame(tab_set[2],relief = "flat",height = 270,bg = "#aad2ff")
    t_frame.grid(row = 1, column = 0,columnspan = 3,padx = 3, pady = 5,sticky = "ew")

    tool.bind('<Button-1>', handle_click_yp)

    #treeにplayerの表示
    for n in config.options("tool"):
        p = config.get("tool",n).split(",")
        tool.insert("","end",values = (n,p[0],p[1]))


    t_add_button    = tk.Button(t_frame,
                                text    = "追加",
                                width   = "6",
                                height  = "1",
                                font    = ("",10),
                                command = lambda : t_add_item())

    t_edit_button    = tk.Button(t_frame,
                              text    = "上書き",
                              width   = "6",
                              height  = "1",
                              font    = ("",10),
                              command = lambda : t_edit())

    t_del_button    = tk.Button(t_frame,
                                text    = "削除",
                                width   = "6",
                                height  = "1",
                                font    = ("",10),
                                command = lambda : t_delete())



    t_up_button     = tk.Button(t_frame,text  = "∧",width = 5,font = ("",10),command = lambda : t_up())
    t_down_button   = tk.Button(t_frame,text  = "∨",width = 5,font = ("",10),command = lambda : t_down())

    t_add_label     = tk.Label (t_frame,text  = "ツール名",font=("",10),bg = "#aad2ff")
    t_add_name      = tk.Entry (t_frame,width = 20,font = ("",11))

    t_path = tk.Entry (t_frame,width = 43,font = ("",10))
    t_pathb = tk.Button(t_frame,
                        text    = "選択",
                        width   = "6",
                        height  = "1",
                        font    = ("",10),
                        command = lambda : tool_path())


    t_arg_label = tk.Label (t_frame,text  = "引数",font=("",10),bg = "#aad2ff")
    t_arg = tk.Entry (t_frame,width = 30,font = ("",10))


    t2_frame = tk.LabelFrame(t_frame,width = 372,height = 123,text = "引数",bg = "#aad2ff")
    t_frame_label = tk.Label (t2_frame,
                              text  = "$0=チャンネル名    $1=ID    $2=TIP    $3=コンタクトURL\n"
                                    + "$9=Type    $Z=Host:port    $z=Host:potr(2)    $$=$\n"
                                    + "$X=プレイリストURL(http://Host:port/pls/ID?tip=TIP)\n"
                                    + "$x=プレイリストURL(http://IP:port/pls/ID?tip=TIP)\n"
                                    + "$Y=ストリームURL(http://Host:port/stream/ID.Type)\n"
                                    + "$Y=ストリームURL(http://IP:port/stream/ID.Type)\n"
                                    + "$W=プレイリストURL(http://Host:port(2)/pls/ID?tip=TIP)",
                              justify = "left",
                              font=("",10),
                              bg = "#aad2ff")

    tt_frame = tk.Frame(tab_set[2],relief = "flat",height = 50)
    tt_frame.grid(row = 2, column = 0,columnspan = 3, sticky = "nsew")

    t_ok_button     = tk.Button(tt_frame,text  = "OK",width = 10,font = ("",10),command = lambda : t_ok())

    t_cancel_button = tk.Button(tt_frame,text  = "キャンセル",width =10,font = ("",10),command = lambda : exit())


    t_add_button.place (x =  5, y =  8)
    t_edit_button.place(x = 70, y =  8)
    t_del_button.place (x =135, y =  8)
    t_up_button.place  (x =270, y =  8)
    t_down_button.place(x =327, y =  8)

    t_add_label.place  (x =  5, y =  38)
    t_add_name.place   (x = 65, y =  38)
    t_path.place       (x =  5, y =  66)
    t_pathb.place      (x =320, y =  63)
    t_arg_label.place  (x =  7, y =  94)
    t_arg.place        (x = 50, y =  94)
    t2_frame.place     (x =  5, y = 145)
    t_frame_label.place(x =  0, y =   0)

    t_ok_button.place     (x =217, y = 0)
    t_cancel_button.place (x =307, y = 0)

    tool.bind("<<TreeviewSelect>>", t_set_click)


#YP タブ作成
def new_tab():
    global ch_list_all
    global ch_list
    global yp_tab

    def ch_list_click(event):
        if len(ch_list_all.selection()) == 0:
            return
        for item in ch_list_all.selection():
##            m = (item, ch_list_all.item(item)) 何でitemで取るとSTR型の数字がINT型になってるねん!最初の0が消える”
            a = ch_list_all.set(item)
        text.config(state = "normal")
        try:
            text.delete("1.0", tk.END)
        except:
            pass
        t = (a["ch_name"]+"   "
            +a["listener"]+" "
            +a["bitrate"]+"kbps  "
            +a["time"]+"  "
            +a["yp"]+"  "
            +a["type"]+"\n"
            +a["detail"])

        text.insert(tk.END,t)
        text.config(state = "disabled")

    def ch_list_s(event,n):
        if len(ch_list[n].selection()) == 0:
            return
        for item in ch_list[n].selection():
            a = ch_list[n].set(item)
        text.config(state = "normal")
        try:
            text.delete("1.0", tk.END)
        except:
            pass
        t = (a["ch_name"]+" "
            +a["listener"]+" "
            +a["bitrate"]+"kbps "
            +a["time"]+" "
            +a["type"]+"\n"
            +a["detail"])

        text.insert(tk.END,t)
        text.config(state = "disabled")

    tab = []
    ch_list = []
    scrollbary = []
    scrollbarx = []

    yp_tab = ttk.Notebook(chlist_tab)

    #すべてtab
    all = tk.Frame(yp_tab,background="#ffffff")
    yp_tab.add(all, text = "すべて".ljust(6))

    ch_list_all = ttk.Treeview(all,
                               columns        = col,
                               show           = "headings",
                               selectmode     = "browse",
                               displaycolumns = col2)


    scrollbary_all = ttk.Scrollbar(all, orient=tk.VERTICAL,command=ch_list_all.yview)
    scrollbarx_all = ttk.Scrollbar(all, orient=tk.HORIZONTAL,command=ch_list_all.xview)
    scrollbary_all.pack(fill = "y", side = "right")
    scrollbarx_all.pack(fill = "x", side = "bottom")

    c_size_all = config.get("column_size","all").split(",")

    ch_list_all.column("d"       , width = int(c_size_all[0] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("new"     , width = int(c_size_all[1] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("ch_name" , width = int(c_size_all[2] ),anchor=tk.W,stretch = "False")
    ch_list_all.column("detail"  , width = int(c_size_all[3] ),anchor=tk.W,stretch = "False")
    ch_list_all.column("listener", width = int(c_size_all[4] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("bitrate" , width = int(c_size_all[5] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("time"    , width = int(c_size_all[6] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("type"    , width = int(c_size_all[7] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("yp"      , width = int(c_size_all[8] ),anchor=tk.CENTER,stretch = "False")
    ch_list_all.column("contact" , width = int(c_size_all[9] ),anchor=tk.W,stretch = "False")
    ch_list_all.column("id"      , width = int(c_size_all[10]),anchor=tk.W,stretch = "False")
    ch_list_all.column("tip"     , width = int(c_size_all[11]),anchor=tk.W,stretch = "False")

    ch_list_all.heading("d"        , text = "D")
    ch_list_all.heading("new"      , text = "新")
    ch_list_all.heading("ch_name"  , text = "チャンネル名")
    ch_list_all.heading("detail"   , text = "詳細")
    ch_list_all.heading("listener" , text = "リスナー数")
    ch_list_all.heading("bitrate"  , text = "bit rate")
    ch_list_all.heading("time"     , text = "配信時間")
    ch_list_all.heading("type"     , text = "type")
    ch_list_all.heading("yp"       , text = "YP")
    ch_list_all.heading("contact"  , text = "contact URL")
    ch_list_all.heading("id"       , text = "ID")
    ch_list_all.heading("tip"      , text = "IP")

    ch_list_all.config(yscrollcommand=scrollbary_all.set)
    ch_list_all.config(xscrollcommand=scrollbarx_all.set)

    ch_list_all.pack(side = tk.LEFT,expand=1, fill='both')

    ch_list_all.bind("<<TreeviewSelect>>", ch_list_click)
    ch_list_all.bind("<Double-Button-1>",select)
    ch_list_all.bind('<Button-3>',popup)
    ch_list_all.bind("<MouseWheel>", mouse_y_scroll)

    #YP別tab
    for n in range(conf.yp_names(config)[1]):
        tab.append(n)
        ch_list.append(n)
        scrollbarx.append(n)
        scrollbary.append(n)

        tab[n] = tk.Frame(yp_tab,relief = "flat",background="#ffffff")
        tab_name = conf.get_yp(config,n)
        yp_tab.add(tab[n], text = tab_name[0].ljust(6))
        ch_list[n] = ttk.Treeview(tab[n],
                                  columns        = col,
                                  show           = "headings",
                                  selectmode     = "browse",
                                  displaycolumns = col2)

        scrollbary[n] = ttk.Scrollbar(tab[n], orient=tk.VERTICAL,command=ch_list[n].yview)
        scrollbarx[n] = ttk.Scrollbar(tab[n], orient=tk.HORIZONTAL,command=ch_list[n].xview)
        scrollbary[n].pack(fill = "y", side = "right")
        scrollbarx[n].pack(fill = "x", side = "bottom")

        ch_list[n].column("d"       , width = int(tab_name[3]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("new"     , width = int(tab_name[4]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("ch_name" , width = int(tab_name[5]),anchor=tk.W,stretch = "False")
        ch_list[n].column("detail"  , width = int(tab_name[6]),anchor=tk.W,stretch = "False")
        ch_list[n].column("listener", width = int(tab_name[7]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("bitrate" , width = int(tab_name[8]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("time"    , width = int(tab_name[9]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("type"    , width = int(tab_name[10]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("yp"      , width = int(tab_name[11]),anchor=tk.CENTER,stretch = "False")
        ch_list[n].column("contact" , width = int(tab_name[12]),anchor=tk.W,stretch = "False")
        ch_list[n].column("id"      , width = int(tab_name[12]),anchor=tk.W,stretch = "False")
        ch_list[n].column("tip"     , width = int(tab_name[13]),anchor=tk.W,stretch = "False")

        ch_list[n].heading("d"        , text = "D")
        ch_list[n].heading("new"      , text = "新")
        ch_list[n].heading("ch_name"  , text = "チャンネル名")
        ch_list[n].heading("detail"   , text = "詳細")
        ch_list[n].heading("listener" , text = "リスナー数")
        ch_list[n].heading("bitrate"  , text = "bit rate")
        ch_list[n].heading("time"     , text = "配信時間")
        ch_list[n].heading("type"     , text = "type")
        ch_list[n].heading("yp"       , text = "YP")
        ch_list[n].heading("contact"  , text = "contact URL")
        ch_list[n].heading("id"       , text = "ID")
        ch_list[n].heading("tip"      , text = "IP")

        ch_list[n].config(yscrollcommand=scrollbary[n].set)
        ch_list[n].config(xscrollcommand=scrollbarx[n].set)

        ch_list[n].pack(side = tk.LEFT,expand=1, fill='both')

        ch_list[n].bind("<<TreeviewSelect>>",lambda event: ch_list_s(event,yp_tab.tabs().index(yp_tab.select())-1))
        ch_list[n].bind("<Double-Button-1>",lambda event: select_s(event,yp_tab.tabs().index(yp_tab.select())-1))
        ch_list[n].bind('<Button-3>',lambda event: popup_s(event,yp_tab.tabs().index(yp_tab.select())-1))
        ch_list[n].bind("<MouseWheel>",lambda event: mouse_y_scroll_s(event,yp_tab.tabs().index(yp_tab.select())-1))

    ttk.Style().configure("Treeview.Heading", font=(None, 9))
    yp_tab.pack(expand=1, fill='both',padx = 2,pady = 2)

def play(list,player,arg,type):
    type = type.lower()
    port = config.get("peca","peca_port").split(":")[1]
    arg = arg.replace("$X","http://" + config.get("peca","peca_port") + "/pls/" + str(list["id"]) + "?tip=" + str(list["tip"]))
    arg = arg.replace("$x","http://127.0.0.1:" + port + "/pls/" + str(list["id"]) + "?tip=" + str(list["tip"]))
    arg = arg.replace("$Y","http://" + config.get("peca","peca_port") + "/stream/" + str(list["id"]) + "." + type)
    arg = arg.replace("$y","http://127.0.0.1:" + port + "/stream/" + str(list["id"]) + "." + type)
    arg = arg.replace("$W","http://" + config.get("peca","peca_port2") + "/pls/" + str(list["id"]) + "?tip=" + str(list["tip"]))
    arg = arg.replace("$0",str(list["ch_name"]))
    arg = arg.replace("$1",str(list["id"]))
    arg = arg.replace("$2",str(list["tip"]))
    arg = arg.replace("$3",str(list["contact"]))
    arg = arg.replace("$9",str(list["type"]))
    arg = arg.replace("$Z",config.get("peca","peca_port"))
    arg = arg.replace("$z",config.get("peca","peca_port2"))
    arg = arg.replace("$$","$")
    print("start:",player,arg)
    try:
        subprocess.Popen(player + " " + arg)
    except:
        return

#チャンネルリストダブルクリック
def select(event):
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    for n in config.options("player"):
        c_type = config.get("player",n).split(",")
        if not str(list["type"].lower()) in str(c_type[2].lower()):
            continue
        else:
            player = c_type[0]        #マッチしたプレイヤー
            a = str(c_type[1])        #引数
            play(list,player,a,list["type"])

def select_s(event,n):
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    for n in config.options("player"):
        c_type = config.get("player",n).split(",")
        if not str(list["type"].lower()) in str(c_type[2].lower()):
            continue
        else:
            player = c_type[0]        #マッチしたプレイヤー
            a = str(c_type[1])        #引数
            play(list,player,a,list["type"])
#mainGUI
config = conf.config()
col = ["d","new","ch_name","detail","listener","bitrate","time","type","yp","contact","id","tip"]
col2= ["new","d","ch_name","detail","listener","bitrate","time","type","yp","contact","id","tip"]  #testカラムの順番等

root = tk.Tk()
root.title("YP")
root.resizable(width = True, height = True)
window = (config.get("SETTING","window_x") + "x"
        + config.get("SETTING","window_y") + "+"
        + config.get("SETTING","position_x") + "+"
        + config.get("SETTING","position_y"))
root.geometry(window)

top_frame = tk.Frame(root,bd = 2,relief = "flat")

update_button = tk.Button(top_frame,text="更新",
                          height  = "1",
                          width   = "8",
                          relief  = "raised",
                          font    = ("",10),
                          command = lambda: get_once())

mylist_button = tk.Button(top_frame,text="フィルター",
                          height  = "1",
                          width   = "8",
                          relief  = "raised",
                          font    = ("",10),
                          command = lambda: set_filter())

setting_button = tk.Button(top_frame,text="設定",
                           height  = "1",
                           width   = "8",
                           relief  = "raised",
                           font    = ("",10),
                           command = lambda: settings())

sort_filter_show = tk.BooleanVar()
sort_listener_show = tk.BooleanVar()
sort_filter = tk.Checkbutton(top_frame,
                             variable = sort_filter_show,
                             text = "フィルターでソート",
                             font = ("",10),
                             height = 1)

sort_listener = tk.Checkbutton(top_frame,
                               variable = sort_listener_show,
                               text = "リスナー数でソート",
                               font = ("",10),
                               height = 1)

if config.get("SETTING","sort_filter") == "True":
    sort_filter_show.set("True")
else:
    sort_filter_show.set("False")
if config.get("SETTING","sort_listener") == "True":
    sort_listener_show.set("True")
else:
    sort_listener_show.set("False")
update_button.pack (side = "left", anchor ="n",padx = 3,pady = 3)
mylist_button.pack (side = "left", anchor ="n",padx = 3,pady = 3)
setting_button.pack(side = "right",anchor ="n",padx = 3,pady = 3)
sort_filter.pack   (side = "left", anchor ="n",padx = 3,pady = 3)
sort_listener.pack (side = "left", anchor ="n",padx = 3,pady = 3)

chlist_tab = tk.Frame(root,bd = 2,relief = "flat")

text_frame = tk.Frame(root,bd = 2,relief = "flat")
text = tk.Text (text_frame,width = 10,
                height = 3,
                font = ("",10),
                state = "disabled",
                wrap = "word")
uptime=""
up_time = tk.Label(root,text = uptime,font = ("",10))
sizegrip = ttk.Sizegrip(root)

top_frame.pack  (side = "top",expand = 0,fill = "x")
chlist_tab.pack (side = "top",expand = 1,fill = 'both')
text_frame.pack (side = "top",fill = "x")
text.pack       (side = "top",expand = 1,fill = "x")
up_time.pack    (side = "left",anchor = "w")
sizegrip.pack   (side = "bottom",anchor = "e")

#右クリックポップアップUI
def browser():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    if list["contact"] in "http":
        return
    webbrowser.open(list['contact'])

def clip_ch():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    pyperclip.copy(list['ch_name'])

def clip_detail():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    pyperclip.copy(list['detail'])

def clip_contact():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    pyperclip.copy(list['contact'])

def clip_tip():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    pyperclip.copy(list['tip'])

def clip_all():
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    pyperclip.copy(str(list['ch_name'] +" "
                      +list['detail']  +" "
                      +list['listener']+" "
                      +list['bitrate'] +" "
                      +list['time']    +" "
                      +list['type']    +" "
                      +list['yp']      +" "
                      +list['contact'] +" "
                      +list['id']      +" "
                      +list['tip']))

def browser_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    if list["contact"] in "http":
        return
    webbrowser.open(list["contact"])

def clip_ch_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    pyperclip.copy(list['ch_name'])

def clip_detail_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    pyperclip.copy(list['detail'])

def clip_contact_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    pyperclip.copy(list["contact"])

def clip_tip_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    pyperclip.copy(list['tip'])

def clip_all_s():
    n = yp_tab.index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    pyperclip.copy(str(list['ch_name'] +" "
                      +list['detail']  +" "
                      +list['listener']+" "
                      +list['bitrate'] +" "
                      +list['time']    +" "
                      +list['type']    +" "
                      +list['yp']      +" "
                      +list['contact'] +" "
                      +list['id']      +" "
                      +list['tip']))

#右クリックメニュー
def popup(event):
    id = ch_list_all.identify("item", event.x, event.y)
    ch_list_all.selection_set(id)
    if not id:
        return
    menu_top.post(event.x_root,event.y_root)

def popup_s(event,n):
    id = ch_list[n].identify("item", event.x, event.y)
    ch_list[n].selection_set(id)
    if not id:
        return
    menu_top_s.post(event.x_root,event.y_root)

menu_top = tk.Menu(root,tearoff=False)
menu_2 = tk.Menu(menu_top,tearoff=0)
menu_3 = tk.Menu(menu_top,tearoff=0)
menu_top.add_command (label = "コンタクトURLを開く".ljust(20),command = browser,font = (" ",10))
menu_top.add_separator()
menu_top.add_cascade(label = "コピー",menu=menu_2,font = (" ",10))
menu_top.add_separator()
menu_top.add_cascade(label = "ツール",menu=menu_3,font = (" ",10))


menu_2.add_command(label = "チャンネル名".ljust(20),command = clip_ch,font = (" ",10))
menu_2.add_command(label = "詳細",command = clip_detail,font = (" ",10))
menu_2.add_command(label = "コンタクトURL",command = clip_contact,font = (" ",10))
menu_2.add_command(label = "tip",command = clip_tip,font = (" ",10))
menu_2.add_command(label = "すべて",command = clip_all,font = (" ",10))

def tools(nn):
    h = config.get("tool",nn).split(",")
    for item in ch_list_all.selection():
        if not item:
            return
    list = ch_list_all.set(item)
    play(list,h[0],h[1],list["type"])

for n in config.options("tool"):
    menu_3.add_command(label = n.ljust(20),command = lambda arg=n: tools(arg))

menu_top_s = tk.Menu(root,tearoff=False)
menu_2_s = tk.Menu(menu_top_s,tearoff=0)
menu_3_s = tk.Menu(menu_top_s,tearoff=0)
menu_top_s.add_command (label = "コンタクトURLを開く".ljust(20),command = browser_s,font = (" ",10))
menu_top_s.add_separator()
menu_top_s.add_cascade(label = "コピー",menu=menu_2_s,font = (" ",10))
menu_top_s.add_separator()
menu_top_s.add_cascade(label = "ツール",menu=menu_3_s,font = (" ",10))

menu_2_s.add_command(label = "チャンネル名".ljust(20),command = clip_ch_s,font = (" ",10))
menu_2_s.add_command(label = "詳細",command = clip_detail_s,font = (" ",10))
menu_2_s.add_command(label = "コンタクトURL",command = clip_contact_s,font = (" ",10))
menu_2_s.add_command(label = "tip",command = clip_tip_s,font = (" ",10))
menu_2_s.add_command(label = "すべて",command = clip_all_s,font = (" ",10))

def tools_s(nn):
    print(nn)
    h = config.get("tool",nn).split(",")
    n = yp_tab.tabs().index(yp_tab.select())-1
    for item in ch_list[n].selection():
        if not item:
            return
    list = ch_list[n].set(item)
    play(list,h[0],h[1],list["type"])

for n in config.options("tool"):
    menu_3_s.add_command(label = n.ljust(20),command = lambda arg=n: tools_s(arg))

def mouse_y_scroll(event):
    if event.delta > 0:
        ch_list_all.yview_scroll(-2, 'units')
    elif event.delta < 0:
        ch_list_all.yview_scroll(2, 'units')
def mouse_y_scroll_s(event,n):
    if event.delta > 0:
        ch_list[n].yview_scroll(-2, 'units')
    elif event.delta < 0:
        ch_list[n].yview_scroll(2, 'units')

update2 = 0
new_tab()
get_start()
root.after(1000, show_yp)

#■■■■■■■■■■treeviewのバグ修正■■■■■■■■■■
style = ttk.Style()
style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()