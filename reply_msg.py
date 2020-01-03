#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# #    File: reply_msg.py
# #    Project: Mocha-L/WechatPCAPI 
# #    Author: zzy
# #    mail: elliot.bia.8989@outlook.com
# #    github: https://github.com/elliot-bia
# #    Date: 2019-12-09 14:59:42
# #    LastEditors: zzy
# #    LastEditTime: 2020-01-03 10:03:11
# #    ---------------------------------
# #    Description: 对Mocha-L的WechatPCAPI进行调用,  实现功能: 自动接受的个人信息, 指定群信息发送到指定admin微信, 并且通过回复序列号(空格)信息进行回复


###
# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : Leon
# @Email   : 1446684220@qq.com
# @File    : test.py
# @Desc    :
# @Software: PyCharm

from WechatPCAPI import WechatPCAPI
import time
import logging
from queue import Queue
import threading


logging.basicConfig(level=logging.INFO)
queue_recved_message = Queue()


def on_message(message):
    queue_recved_message.put(message)


# 控制台微信
admin_wx = 'wxid_xxxx'
# 单人黑名单列表
single_block_list = ['wxid_xxxx']  # 最好把控制台微信加进去
# 群组接受名单
group_receive_list = ['xxxxxxx@chatroom']
# 创建remark_name字典
dict_remark_name = {}
# 定义信息ID字典
dict_msg_ID = {}
# 全局
ID_num = 0


def deal_remark_name(message):
    ###
    # #    描述: 字典好友信息, 每次启动微信都重新获取一份, 注重remark_name, 其他不管
    # #    description: save wechat's friends message, reload file when wechat start everytime
    # #    param: {message}
    # #    usage:
    # #    return: none
    ###
    wx_id = message.get('data', {}).get('wx_id', '')
    remark_name = message.get('data', {}).get('remark_name', '')
    dict_remark_name[wx_id] = remark_name


# 消息处理 分流
def thread_handle_message(wx_inst):
    global ID_num
    while True:
        message = queue_recved_message.get()
        print(message)
        
        # 坑点: if和elif 慎用

        # 本地保存friends信息, 重点remark_name
        try:
            if 'friend::person' in message.get('type'):
                deal_remark_name(message)
        except:
            pass

        
        # 单人消息
        try:
            if 'msg::single' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                # 判断微信id, 黑名单
                from_wxid = message.get('data', {}).get('from_wxid', '')
                data_type = message.get('data', {}).get('data_type', '') 
                if send_or_recv[0] == '0':
                    # 0是收到的消息 1是发出的 对于1不要再回复了 不然会无限循环回复
                    
                        
                    if (from_wxid not in single_block_list) and (from_wxid in dict_remark_name.keys()):
                        # 判断微信id, 黑名单, 并且屏蔽公众号
                        if data_type[0] == '1':
                        # 只接受文字
                            msg_content = message.get('data', {}).get('msg', '')
                            wx_inst.send_text(admin_wx, '微信收到好友消息\n  {} : {} \n信息ID {}'.format(
                                dict_remark_name[from_wxid], msg_content, ID_num))
                        else:
                            wx_inst.send_text(admin_wx, '微信收到好友{}一张图片或表情包 \n信息ID {}'.format(
                                dict_remark_name[from_wxid], ID_num))

                        # 弄一个字典, 保存信息ID, 通过回复ID+信息进行回复给好友
                        dict_msg_ID[ID_num] = from_wxid
                        ID_num = ID_num + 1
                    
                
                # 进行回复
                if (send_or_recv[0] == '0') and (from_wxid in admin_wx):
                    msg_content = message.get('data', {}).get('msg', '')
                    try:
                        reply_msage_ID = msg_content.split(' ', 1)[0]
                        reply_msage = msg_content.split(' ', 1)[1]

                        # print(dict_msg_ID[int(reply_msage_ID)])
                        # print(type(dict_msg_ID[reply_msage_ID]))
                        # print(reply_msage)
                        # print(type(reply_msage))

                        wx_inst.send_text(str(dict_msg_ID[int(reply_msage_ID)]), str(reply_msage))
                    except: 
                        wx_inst.send_text(admin_wx, '没事干控制端不要发信息')
        except:
            pass
                    

        # 接受群组信息
        try: 
            if 'msg::chatroom' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                data_type = message.get('data', {}).get('data_type', '') 
                # 判断群组id, 黑名单
                from_chatroom_wxid = message.get(
                    'data', {}).get('from_chatroom_wxid', '')
                if send_or_recv[0] == '0':
                    
                    if from_chatroom_wxid in group_receive_list:
                        if data_type[0] == '1':
                            msg_content = message.get('data', {}).get('msg', '')
                            from_wxid = message.get('data', {}).get('from_member_wxid', '')
                            from_chatroom_wxid = message.get('data', {}).get('from_chatroom_wxid', '')
                            from_chatroom_nickname = message.get('data', {}).get('from_chatroom_nickname', '')
                            wx_inst.send_text(admin_wx, '微信收到群 {} 消息\n {} : {}  \n信息ID {}'.format(from_chatroom_nickname, 
                                dict_remark_name[from_wxid], msg_content, ID_num))
                        else:
                            from_wxid = message.get('data', {}).get('from_member_wxid', '')
                            from_chatroom_wxid = message.get('data', {}).get('from_chatroom_wxid', '')
                            from_chatroom_nickname = message.get('data', {}).get('from_chatroom_nickname', '')
                            wx_inst.send_text(admin_wx, '微信收到群 {} 消息成员{} \n一张图片/表情   \n信息ID {}'.format(from_chatroom_nickname, 
                                dict_remark_name[from_wxid], ID_num))
                            
                        # 弄一个字典, 保存信息ID, 通过回复ID+信息进行回复给好友
                        dict_msg_ID[ID_num] = from_chatroom_wxid
                        ID_num = ID_num + 1
        except:
            pass


def main():
    wx_inst = WechatPCAPI(on_message=on_message, log=logging)
    wx_inst.start_wechat(block=True)

    while not wx_inst.get_myself():
        time.sleep(5)

    print('登陆成功')

    threading.Thread(target=thread_handle_message, args=(wx_inst,)).start()

    time.sleep(10)
    wx_inst.send_text(to_user=admin_wx, msg='脚本开始')

if __name__ == '__main__':
    main()
