import json

def zip_arrays_with_condition(condition, *arrays):
    result_array = filter(condition, zip(*arrays))
    return result_array

def string_to_num(unicode_string):
    string  = unicode_string.encode()
    if string.find(',') != -1:
        string = string.replace(',', '')
    float_number = int(string)
    return float_number

def debug_log(string):
    log = open('debug', 'a')
    log.write(string + "\n")
    log.close()

def debug_log_json(string):
    debug_log(json.dumps(string))
