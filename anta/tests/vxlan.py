"""
Test functions related to VXLAN
"""
from jsonrpclib import jsonrpc

def verify_vxlan(device, enable_password):
    """
    Verifies the interface vxlan 1 status is up/up.

    Args:
        device (jsonrpclib.jsonrpc.ServerProxy): Instance of the class jsonrpclib.jsonrpc.ServerProxy with the uri f'https://{username}:{password}@{ip}/command-api'.
        enable_password (str): Enable password.

    Returns:
        bool: `True` if the interface vxlan 1 status is up/up.
        `False` otherwise.

    """
    try:
        response = device.runCmds(1, ['show interfaces description | include Vx1'], 'text')
    except jsonrpc.AppError:
        return None
    try:
        if response[0]['output'].count('up') == 2:
            return True
        return False
    except KeyError:
        return None

def verify_vxlan_config_sanity(device, enable_password):
    """
    Verifies there is no VXLAN config-sanity warnings.

    Args:
        device (jsonrpclib.jsonrpc.ServerProxy): Instance of the class jsonrpclib.jsonrpc.ServerProxy with the uri f'https://{username}:{password}@{ip}/command-api'.
        enable_password (str): Enable password.

    Returns:
        bool: `True` if there is no VXLAN config-sanity warnings.
        `False` otherwise.
    """
    try:
        response = device.runCmds(1, ['show vxlan config-sanity'], 'json')
    except jsonrpc.AppError:
        return None
    try:
        if len(response[0]['categories']) == 0:
            return None
        for category in response[0]['categories']:
            if category in ['localVtep', 'mlag']:
                if response[0]['categories'][category]['allCheckPass'] is not True:
                    return False
        return True
    except KeyError:
        return None
    
def verify_vlan_to_vni_mapping(device, enable_password, vlans=None, offset=None):
    """
    Verifies the vlan to vni mappings matches as expected.

    Args:
        device (jsonrpclib.jsonrpc.ServerProxy): Instance of the class jsonrpclib.jsonrpc.ServerProxy with the uri f'https://{username}:{password}@{ip}/command-api'.
        enable_password (str): Enable password.
        vlans (int[]): List of VLANs which should have a VNI mapping.
        offset (int): Offset for the VNI, calculation is int(vlan) + int(offset).

    Returns:
        bool: `True` if all vlan to vni mappings are correct.
        `False` otherwise.
    """
    if not vlans:
        return None
    if not offset:
        return None
    
    try:
        response = device.runCmds(1, ['show interfaces vxlan 1'], 'json')
    except jsonrpc.AppError:
        return None
    try:
        for vlan in vlans:
            if str(vlan) in response[0]['interfaces']['Vxlan1']['vlanToVniMap']:
               if int(response[0]['interfaces']['Vxlan1']['vlanToVniMap'][str(vlan)]['vni']) != int(vlan) + int(offset):
                    return False
            else:
               return False
        return True
    except KeyError:
        return None

def verify_vxlan_floodlist(device, enable_password, vteps=None):
    """
    Verifies the VTEPs are in the floodlist

    Args:
        device (jsonrpclib.jsonrpc.ServerProxy): Instance of the class jsonrpclib.jsonrpc.ServerProxy with the uri f'https://{username}:{password}@{ip}/command-api'.
        enable_password (str): Enable password.
        vteps (str[]): List of VTEP IPs which should be in the floodlist.

    Returns:
        bool: `True` if all VTEPs are in the floodlist (except the local one).
        `False` otherwise.
    """
    if not vteps:
        return None
    
    try:
        response = device.runCmds(1, ['show vxlan vtep'], 'json')
    except jsonrpc.AppError:
        return None
    try:
        for vtep in vteps:
            try:
                response2 = device.runCmds(1, ['show ip interface ' + vtep], 'json')
            except jsonrpc.AppError:
                return None
            if len(response2[0]['interfaces']) == 0:
                if vtep not in response[0]['interfaces']['Vxlan1']['vteps']:
                    return False
        if len(vteps)-1 == len(response[0]['interfaces']['Vxlan1']['vteps']):
            return True
        else:
            return False
    except KeyError:
        return None
