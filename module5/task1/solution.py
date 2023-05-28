def nmac(key, message):
    return h(key + h(key + message))
