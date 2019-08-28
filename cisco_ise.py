#!/usr/bin/env python3

'''
Author:  Danny Finein (Red River Technologies)

Used to read-only interface with Cisco 2.2 - 2.6
'''

import requests
import json
# USE THIS TO DISABLE THAT THE HTTPS IS UNVERIFIED WARNING
import urllib3


# IMPORT ISE Templates
user_add_template = "ise_templates/ise_add_user.json"

true = "true"
false = "false"


class API(object):

    def __init__(self, ise_node):
        self.node = ise_node
        self.url = 'https://{0}:9060/ers/'.format(self.node)
        self.is_connected = False
        self.username = ""
        self.password = ""
        self.ise = requests.session()

    def authenticate(self, ise_user, ise_password, verify=False, disable_warnings=True, timeout=2):
        self.username = ise_user
        self.password = ise_password
        self.ise.auth = (ise_user, ise_password)
        self.ise.verify = verify
        if (disable_warnings):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.timeout = timeout
        self.ise.headers.update({'Connection': 'keep_alive'})
        self.ise.headers.update({'Accept' : 'application/json'})
        self.ise.headers.update({'Content-Type': 'application/json'})
        # Needed a check to make sure this was working - internal user has existed since 2.2
        if (self.ers_get('config/internaluser/').status_code == 200):
            self.is_connected = True
            return True
        else:
            return False

    def delete_token(self):
        self.username = ""
        self.password = ""
        self.is_connected = False

    def ers_get(self, url):
        response = self.ise.get('{0}{1}'.format(self.url,url))
        return response

    def ers_post(self, url, data):
        response = self.ise.post('{0}{1}'.format(self.url,url), data=data, timeout=5)
        return response

    def ers_put(self, url, data):
        response = self.ise.put('{0}{1}'.format(self.url,url), data=data, timeout=5)
        return response

    def ers_delete(self, url):
        response = self.ise.delete('{0}{1}'.format(self.url,url))
        return response

    def get_config(self, resource, resource_id = "") -> list:
        # resource can be one of the following:
        #
        # ANC Endpoint:                         ancendpoint
        # ANC Policy:                           ancpolicy
        # Active Directory:                     activedirectory
        # Admin User:                           adminuser
        # Advanced Customization Global Setting:portalglobalsetting
        # Allowed Protocols:                    allowedprotocols
        # Authorization Profile:                authorizationprofile
        # BYOD Portal:                          byodportal
        # Certificate Template:                 certificatetemplate
        # Certificate Profile:                  certificateprofile
        # Downloadable ACL:                     downloadableacl
        # Egress Matrix Cell:                   egressmatrixcell
        # End Point:                            endpoint
        # EndPoints Identity Group:             endpointgroup
        # External Radius Server:               externalradiusserver
        # Guest Location:                       guestlocation
        # Guest SMTP Notification Config:       guestnotificationsettings
        # Guest SSID:                           guestssid
        # Guest Type:                           guesttype
        # Guest User:                           guestuser
        # Hotspot Portal:                       hotspotportal
        # IP to SGT Mapping:                    sgmapping
        # IP to SGT Mapping Group:              sgmappinggroup
        # ISE Service Information:              service
        # Identity Group:                       identitygroup
        # Identity Sequence:                    idstoresequence
        # Internal User:                        internaluser
        # My Device Portal:                     mydeviceportal
        # Native Supplicant Profile:            nspprofile
        # Network Device:                       networkdevice
        # Network Device Group:                 networkdevicegroup
        # Node Details:                         node
        # PSN Node Details w/Radius Service:    sessionservicenode
        # Portal:                               portal
        # Portal Theme:                         portaltheme
        # Profiler Profile:                     profilerprofile
        # pxGrid Node:                          pxgridnode
        # Radius Server Sequence:               radiusserversequence
        # SMS Server:                           smsprovider
        # SXP Connections:                      sxpconnections
        # SXP Local Bindings:                   sxplocalbindings
        # SXP VPNs:                             sxpvpns
        # Security Groups:                      sgt
        # Security Groups ACL:                  sgacl
        # Security Groups to Virtual Networks:  sgtvnvlan
        # Self Registered Portal:               selfregportal
        # Sponsor Portal:                       sponsorgroup
        # Sponsor Group Member:                 sponsorgroupmember
        # Sponsor Portal:                       sponsorportal
        # Sponsored Guest Portal:               sponsoredguestportal
        # TACACS Command Sets:                  tacacscommandsets
        # TACACS External Servers:              tacacsexternalservers
        # TACACS Profile:                       tacacsprofile
        # TACACS Server Sequence:               tacacsserversequence
        response = self.ers_get('config/{0}/{1}'.format(resource, resource_id))
        if response.status_code == 200:
            if resource_id == "":
                return json.loads(response.text)['SearchResult']['resources']
            else:
                resource_response = json.loads(response.text)
                for i in resource_response:
                    return resource_response[i]
        else:
            return None
