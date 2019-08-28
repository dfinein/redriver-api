#!/usr/bin/env python3

'''
ISE_TUI.py

Author:  Danny Finein

Text Based UI to use with cisco_ise library
Due to Windows limitation of support curses,
This file will only work on *nix machines
'''



import npyscreen
import cisco_ise
from textwrap import wrap
import sys
# import threading
# OR
import time

TUI_bg_image = '''8888888b.               888      8888888b.  d8b
888   Y88b              888      888   Y88b Y8P
888    888              888      888    888
888   d88P .d88b.   .d88888      888   d88P 888 888  888  .d88b.  888d888
8888888P" d8P  Y8b d88" 888      8888888P"  888 888  888 d8P  Y8b 888P"
888 T88b  88888888 888  888      888 T88b   888 Y88  88P 88888888 888
888  T88b Y8b.     Y88b 888      888  T88b  888  Y8bd8P  Y8b.     888
888   T88b "Y8888   "Y88888      888   T88b 888   Y88P    "Y8888  888'''



def json_to_pager(content, indent_level):
    pager_list = []
    if type(content) == dict:
        for i in content:
            pager_list.append("\t"*indent_level + str(i) + ":")
            pager_list += json_to_pager(content[i], (indent_level + 1))
    elif type(content) == list:
        for i in content:
            pager_list += json_to_pager(i, (indent_level + 1))
    else:
        for i in wrap(str(content), 80):
            pager_list.append("\t"*indent_level + i)
    return pager_list



'''
ISE Forms
'''
class ISE_Form(npyscreen.Popup):

    def afterEditing(self):
        global ise
        ise = cisco_ise.API(self.node.value)
        if ise.authenticate(self.username.value, self.password.value):
            self.parentApp.main.banner_message("ISE Authentication Complete")
        else:
            self.parentApp.main.banner_message("ISE Authentication Failure")
        self.parentApp.setNextForm('MAIN')

    def create(self):
        self.node = self.add(npyscreen.TitleText, name = "ISE Server:")
        self.username = self.add(npyscreen.TitleText, name = "Username:")
        self.password = self.add(npyscreen.TitlePassword, name = "Password:")


'''
Main Form With All the Action
'''
ise_config_options = {
                      'ANC Endpoint' : 'ancendpoint',
                      'ANC Policy' : 'ancpolicy',
                      'Active Directory' : 'activedirectory',
                      'Admin User' : 'adminuser',
                      'Advanced Customization Global Setting' : 'portalglobalsetting',
                      'Allowed Protocols' : 'allowedprotocols',
                      'Authorization Profile' : 'authorizationprofile',
                      'BYOD Portal' : 'byodportal',
                      'Certificate Template' : 'certificatetemplate',
                      'Certificate Profile' : 'certificateprofile',
                      'Downloadable ACL' : 'downloadableacl',
                      'Egress Matrix Cell' : 'egressmatrixcell',
                      'End Point' : 'endpoint',
                      'EndPoints Identity Group' : 'endpointgroup',
                      'External Radius Server' : 'externalradiusserver',
                      'Guest Location' : 'guestlocation',
                      'Guest SMTP Notification Config' : 'guestnotificationsettings',
                      'Guest SSID' : 'guestssid',
                      'Guest Type' : 'guesttype',
                      'Guest User' : 'guestuser',
                      'Hotspot Portal' : 'hotspotportal',
                      'IP to SGT Mapping' : 'sgmapping',
                      'IP to SGT Mapping Group' : 'sgmappinggroup',
                      'ISE Service Information' : 'service',
                      'Identity Group' : 'identitygroup',
                      'Identity Sequence' : 'idstoresequence',
                      'Internal User' : 'internaluser',
                      'My Device Portal' : 'mydeviceportal',
                      'Native Supplicant Profile' : 'nspprofile',
                      'Network Device' : 'networkdevice',
                      'Network Device Group' : 'networkdevicegroup',
                      'Node Details' : 'node',
                      'PSN Node Details w/Radius Service' : 'sessionservicenode',
                      'Portal' : 'portal',
                      'Portal Theme' : 'portaltheme',
                      'Profiler Profile' : 'profilerprofile',
                      'pxGrid Node' : 'pxgridnode',
                      'Radius Server Sequence' : 'radiusserversequence',
                      'SMS Server' : 'smsprovider',
                      'SXP Connections' : 'sxpconnections',
                      'SXP Local Bindings' : 'sxplocalbindings',
                      'SXP VPNs' : 'sxpvpns',
                      'Security Groups' : 'sgt',
                      'Security Groups ACL' : 'sgacl',
                      'Security Groups to Virtual Networks' : 'sgtvnvlan',
                      'Self Registered Portal' : 'selfregportal',
                      'Sponsor Portal Group' : 'sponsorgroup',
                      'Sponsor Group Member' : 'sponsorgroupmember',
                      'Sponsor Portal' : 'sponsorportal',
                      'Sponsored Guest Portal' : 'sponsoredguestportal',
                      'TACACS Command Sets' : 'tacacscommandsets',
                      'TACACS External Servers' : 'tacacsexternalservers',
                      'TACACS Profile' : 'tacacsprofile',
                      'TACACS Server Sequence' : 'tacacsserversequence',
                      'EXIT' : 'Exit'
                     }
ise_config_list = []
for i in ise_config_options:
    ise_config_list.append(i)

class MultiLine_Menu(npyscreen.MultiLine):
    def when_value_edited(self):
        if self.value != None:
            if (ise_config_list[self.value] ==  'EXIT'):
                self.parent.parentApp.switchForm(None)
            else:
                try:
                    ise
                    while not ise.is_connected:
                        self.parent.parentApp.switchForm('CONNECT')

                    response = ise.get_config(ise_config_options[ise_config_list[self.value]])
                    response_names = {}
                    try:
                        for i in response:
                            try:
                                response_names[i['name']] = i['id']
                            except KeyError:
                                continue
                            self.parent.update_actions(response_names)
                            self.parent.selection = ise_config_options[ise_config_list[self.value]]
                        self.parent.tui_log("{0} names retrieved".format(ise_config_list[self.value]))
                    except TypeError:
                        self.parent.tui_log("{0} returned no results".format(ise_config_list[self.value]))

                except NameError:
                    self.parent.parentApp.switchForm('CONNECT')

                self.value = None

class MultiLine_Action_Menu(npyscreen.MultiLine):
    def when_value_edited(self):
        if self.value != None:
            while not ise.is_connected:
                self.parent.parentApp.switchForm('CONNECT')

            if (self.parent.selection == 'adminuser'):
                ise_lookup = 'internaluser'
            else:
                ise_lookup = self.parent.selection
            self.parent.update_output(ise.get_config(ise_lookup, self.parent.actions[self.parent.action_menu_options[self.value]]))
            self.value = None

class Box_Menu(npyscreen.BoxTitle):
    _contained_widget = MultiLine_Menu

class Box_Status(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class Box_Action(npyscreen.BoxTitle):
    _contained_widget = MultiLine_Action_Menu

class Box_Pager(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Pager

class Main_Form(npyscreen.FormBaseNew):
    def create(self):
        self.selection = ""
        self.actions = {}
        self.action_menu_options = []

        self.bg_image = self.add(npyscreen.MultiLineEdit, size=8, value = TUI_bg_image, editable = False, \
                                 relx = 3,rely = 2, scroll_exit=True)
        self.banner = self.add(npyscreen.Textfield, value = "", relx = 15, rely = 10 , width = 50 , editable = False, \
                               color = "CURSOR_INVERSE")

        self.menu = self.add(Box_Menu , relx = 1, rely = 11, width = 42, height = 20, values = ise_config_list, \
                             name="MENU")
        self.output = self.add(Box_Status, relx=1, rely=31, width=42, height=13, value="", \
                               editable=False, name="LOG")
        self.action_menu = self.add(Box_Action , relx = 43, rely = 11, width = 96, height = 10 , values = [], \
                                    scroll_exit = True, check_value_change = False, name="ENTRIES")
        self.action_output = self.add(Box_Pager, relx = 43, rely = 21, width = 96, height = 23 , values = [], \
                                      scroll_exit = True, name='OUTPUT')

    def banner_message(self, content):
        self.banner.show_brief_message(content)
        self.tui_log(content)

    def update_actions(self, option_list):
        self.action_menu_options = []
        for i in option_list:
            self.action_menu_options.append(i)
        self.action_menu.values = self.action_menu_options
        self.actions = option_list
        self.display()

    def update_output(self, content):
        display_content = json_to_pager(content, 0)
        self.action_output.values = display_content
        self.display()

    def tui_log(self, content):
        current_output = self.output.value
        self.output.value = "{0}\n{1}".format(content, current_output)
        self.display()

class tuiFormApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.main = self.addForm('MAIN', Main_Form, name = "ISE TUI Interface", columns = 140, lines = 45)
        self.connect = self.addForm('CONNECT', ISE_Form, name = "ISE Connection", columns = 50, lines = 8)

if __name__ == "__main__":
    TUI = tuiFormApp().run()

