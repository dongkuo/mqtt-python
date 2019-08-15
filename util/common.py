import random
import string


def random_str(length):
    """ 生成若干长度的随机字符串
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def merge_dict(dict1, dict2):
    """用dict2中的值覆盖dict1对应key的值
    """
    result = {}
    for k in dict1.keys():
        v = dict1[k]
        if k in dict2:
            v = dict2[k]
        result[k] = v
    return result
