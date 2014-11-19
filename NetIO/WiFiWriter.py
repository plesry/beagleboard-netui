def template(ssid, type, psk, priority):
    if type == 'WPA':
        return 'network={{\n\tssid="{0}"\n\tpsk="{1}"\n\tpriority={2:d}\n}}\n'.format(ssid, psk, priority)
    return ''


def write(pref_file, ap_list):
    try:
        with open(pref_file, 'w') as f:
            # ap is a dict, ap_list is a list of dicts
            for ap in ap_list:
                f.write(template(**ap))
    except IOError as e:
        print(e.strerror)
        return False
    return True
