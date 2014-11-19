import re


def scan_preferences(pref_file):
    content = ""
    with open(pref_file) as f:
        content = f.read()
    return content


def parse_tokens(content):
    delimiters = [
        '\n', '\t', ' ',
        '=', '\"', '}', 'network={']
    r = re.split('|'.join(delimiters), content)
    tokens = [x for x in r if len(x) > 0]
    return tokens


def separate(tokens, num_attr=3):
    wireless_pairs = []
    for i in range(len(tokens) / (2*num_attr)):
        wireless_pairs.append(
            tokens[i*(2*num_attr):(i+1)*(2*num_attr)])
    return wireless_pairs


def compile_info(wireless_pairs):
    networks = []
    for pair in wireless_pairs:
        d = dict()
        d["security"] = "WPA"
        if pair[0] == "ssid":
            d["ssid"] = pair[1]
        if pair[2] == "psk":
            d["psk"] = pair[3]
        if pair[4] == "priority":
            d["priority"] = int(pair[5])
        networks.append(d)
    return networks


def fetch(pref_file):
    content = scan_preferences(pref_file)
    tokens = parse_tokens(content)
    pairs = separate(tokens)
    return compile_info(pairs)
