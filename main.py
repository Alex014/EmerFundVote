#!/usr/bin/kivy
# -*- coding: UTF-8 -*-

#EmerFundVoteApp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix import gridlayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix import textinput
from kivy.uix import popup
from kivy.uix.label import Label

from kivy.lang import Builder
from kivy.app import App
#from time import sleep
#import kivy.clock 

import socket
import sys

import rpcconnet

from kivy.uix.screenmanager import ScreenManager, Screen

kv="""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                size_hint: 1, None
                height:32
                orientation: 'horizontal'
                Label:
                    size_hint: (None, 1)
                    width: 25
                    text: "D1:"
                TextInput:
                    id: d1
                Label:
                    size_hint: None, 1
                    width: 25
                    text: "D2:"
                TextInput:
                    id: d2
                Button:
                    text: 'show'
                    on_press: app.show_vote_table()
            BoxLayout:
                id: votetable

        BoxLayout:
            size_hint: 1, None
            height: 32
            orientation: 'horizontal'
            Button:
                text: 'Settings'
                on_press: app.open_settings()
            Button:
                text: 'Debug'
                on_press: root.manager.current = 'debug'
            Button:
                text: 'Quit'
                on_press: app.stop()

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 32
            Label:
                size_hint: None, 1
                width: 100
                text: "Host:"
            TextInput:
                id: tihost
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 32
            Label:
                size_hint: None, 1
                width: 100
                text: "Add. source:"
                id: lbstate
            ToggleButton:
                group: "gaddsource"
                text: 'Use json'
                id: btjson
            ToggleButton:
                group: "gaddsource"
                text: 'Use local wallet.dat'
                id: btwallet
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 32
            Label:
                size_hint: None, 1
                width: 100
                text: "Sign method:"
                id: lbstate
            ToggleButton
                group: "gsignmethod"
                text: "sign using json api"
                id: tbjson
            ToggleButton
                group: "gsignmethod"
                text: "sign manual"
                id: tbmanual
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 32
            Label:
                text: "Addresses:"
                id: lbstate
                size_hint: None, 1
                width: 100
            Button:
                size_hint: 0.5, 1
                text: 'Rebuild'
                id: btrebuild
                on_press: app.rebuild_addresses_list()
        GridLayout:
            cols: 1
            row_default_height: 32
            id: gladdresses
        Button:
            text: 'Reload config'
            size_hint: 1, None
            height: 32
            on_press: app.gui_load_config()
        Button:
            text: 'Save'
            size_hint: 1, None
            height: 32
            on_press: app.gui_save_config()
        Button:
            size_hint: 1, None
            height: 32
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
<DebugScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint: 1, None
            height: 32
            orientation: 'horizontal'
            Label:
                size_hint: None, 1
                width: 45
                text: "cmd:"
            TextInput:
                size_hint: None, 1
                width: 45
                text: "list"
                id: edit1
            Label:
                size_hint: None, 1
                width: 45
                text: "data:"
            TextInput:
                id: edit2
            Button:
                size_hint: 0.2, 1
                text: 'send'
                on_release: app.send(root.ids.edit1.text,root.ids.edit2.text)
        TextInput:
            id: log
        Button:
            size_hint: 1, None
            height: 32
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
                
"""


# Declare screens
class MenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class DebugScreen(Screen):
    pass


import votesapi

from kivyadd import MessageBox

class EmerFundVoteApp(App):
        		
    def build(self):
        #self.store = JsonStore('aocfg.json')
        #@if self.store.exists('Title'):
        #    print('Title exists:', self.store.get('Title'))
        #    #store.delete('Title')
        #else:
        #    print('NI Title exists:')
        # Create the screen manager

        self.gui=Builder.load_string(kv)
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(DebugScreen(name='debug'))

        self.votesapi=votesapi.votesapi()

        return self.sm

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        pass

    def build_votes_table(self,votes):
        pass
    #======================Конфиги
    def open_settings(self, *largs):
        self.sm.current = 'settings'
        self.gui_load_config()

    def gui_save_config(self):
        #{'jsonrpc':1,'connection':{'host':'128.199.60.197'}}
        self.votesapi.config['connection']['host']= self.sm.get_screen('settings').ids.tihost.text
        if self.sm.get_screen('settings').ids.btwallet.state=='down':
            self.votesapi.config['jsonrpc']=0
        else:
            self.votesapi.config['jsonrpc']=1
        if self.sm.get_screen('settings').ids.tbmanual.state=='down':
            self.votesapi.config['jsonrpc_sign']=0
        else:
            self.votesapi.config['jsonrpc_sign']=1

        gl=self.sm.get_screen('settings').ids.gladdresses
        self.votesapi.config['addresses']=[]
        for c in gl.children:
            #self.sm.get_screen('settings').ids['adr%s'%n].text
            if c.children[0].state=='down':
                self.votesapi.config['addresses'].append(c.children[0].text)

        self.votesapi.save_config()


    def get_addr_btn(self,addr):
        gl=self.sm.get_screen('settings').ids.gladdresses
        for c in gl.children:
            if c.children[0].text==addr:
                return c.children[0]
        return None

    def gui_load_config(self):
        self.votesapi.load_config()
        self.rebuild_addresses_list()
        if self.votesapi.config['connection']:
            self.sm.get_screen('settings').ids.tihost.text = self.votesapi.config['connection']['host']

        if self.votesapi.config['jsonrpc']=='1' or self.votesapi.config['jsonrpc']==1:
            self.sm.get_screen('settings').ids.btjson.state=='down'
        else:
            self.sm.get_screen('settings').ids.btwallet.state=='down'

        #Сбрасываем выделения
        for c in self.sm.get_screen('settings').ids.gladdresses.children:
            c.children[0].state=='normal'

        if 'addresses' in self.votesapi.config:
            for addr in self.votesapi.config['addresses']:
                b=self.get_addr_btn(addr)
                if b is None:
                    self.add_address_panel(len(self.sm.get_screen('settings').ids.gladdresses.children),'???',addr)
                    b=self.get_addr_btn(addr)
                b.state='down'

    def show_vote_table(self):
        #делаем запрос
        #строим грид
        votes = self.votesapi.get_votes()
        if votes:
            self.sm.get_screen('debug').ids.log.text +='\n %s votes received'%len(votes)
            self.build_votes_table(votes)
        return 1

    def send(self,req,data):
        #pass
        #self.sm.get_screen('debug').ids.log.text +='\n send:'+data
        #sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Internet # UDP
        #sock.sendto(data, ("127.0.0.1", 1984))
        import json
        try:
            d=json.loads(data)
        except:
            import sys
            self.sm.get_screen('debug').ids.log.text +='\n wrong data:%s'%sys.exc_info()[1]
            return 0
        resp=self.votesapi.do_request(req,d)
        if resp:
            self.sm.get_screen('debug').ids.log.text +='\n resp:%s'%resp

    def turn_on_json(self):
        import walletconfig
        walletconfig.make_config_connectable()
        MessageBox(parent=self,titleheader='Information: you have to restart the wallet app',message='Для продолжения работы перезапустите кошелек Emercoin', size_hint=(.9,None), size=(0,300))

    def check_rpc_config(self):
        #Подключает конфигурацию доступа к кошельку по json
        #если уже подключено - ничего не делает
        if not rpcconnet.configured():
            if not rpcconnet.init_config():
                #Спрашиваем одобрение включить json и включаем ежели одобрят
                MessageBox(parent=self, titleheader="Do you want to turn JSON RPC server on?", message="""В настоящее время функция доступа к кошельку для других приложнний отключена.
Для получения адресов и подписания голосов требуется включить эту функцию.
Потом ее можно будет отключить.

Включить сервер JSON для текущего кошелька?""", size_hint=(.9,.5), options=({"YES": "turn_on_json()", "NO (CANCEL)": ""}))
                return 0
        return 1
    def get_addresses_list(self,from_wallet=0):
        #получение списка адресов зависит от метода
        #метод определен в from_wallet
        res=[]
        if from_wallet:
            pass
        else:
            if not self.check_rpc_config(): return []
            la=rpcconnet.walreq({"method": "listaccounts","params":[],"jsonrpc": "2.0","id": 0})['result']
            if la:
                for a in la.keys():
                    res.append((a,rpcconnet.walreq({"method": "getaddressesbyaccount","params":[a],"jsonrpc": "2.0","id": 0})['result']))
        return res

    def add_address_panel(self,n,ltext,addr):
        bl=BoxLayout(orientation= 'horizontal',size_hint=(1, None), height=32)
        bl.add_widget(Label(text=ltext,size_hint=(None,1), width=100))
        bl.add_widget(ToggleButton(text=addr,id='adr%s'%n)) #, on_press=self.open_3
        self.sm.get_screen('settings').ids.gladdresses.add_widget(bl)

    def rebuild_addresses_list(self):
        #создание нового списка адресов в
        #import kivy.uix
        #gl=kivy.uix.gridlayout()

        for c in self.sm.get_screen('settings').ids.gladdresses.children:
            pass
        al=self.get_addresses_list(self.sm.get_screen('settings').ids.btwallet.state=='down')
        for a in al:
            #создаем панель высотой 32 пиксела, на ней - чекпокс и метку с адресом
            n=0
            for addr in a[1]:
                self.add_address_panel(n,a[0],addr)
                n+=1

if __name__ == '__main__':
    EmerFundVoteApp().run()