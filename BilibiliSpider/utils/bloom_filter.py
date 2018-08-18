# -*- coding:utf-8 -*-
import sys
import redis
import math
from hashlib import md5

pool = redis.ConnectionPool(host='', port=6379, db=0, password="")
conn = redis.StrictRedis(connection_pool=pool)


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    # 随机种子
    SEEDS = [543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372,
             344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338,
             465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53,
             481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371,
             63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518]

    def __init__(self, capacity=100000000, error_rate=0.000001, conn=None, key='BloomFilter'):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param blockNum: one blockNum for about 90,000,000; if you have more strings for filtering, increase it.
        :param key: the key's name in Redis
        """
        self.bit = math.ceil(capacity * math.log2(math.e) * math.log2(1 / error_rate))  # 需要的总bit位数
        self.hash_counts = math.ceil(math.log1p(2) * self.bit / capacity)               # 需要最少的hash次数
        self.mem = math.ceil(self.bit / 8 / 1024 / 1024)                                # 需要的多少M内存
        self.block_num = math.ceil(self.mem / 512)                                      # 需要多少个512M的内存块,value的第一个字符必须是ascii码，所有最多有256个内存块
        self.bit_size = 1 << 31                                                         # Redis的String类型最大容量为512M，现使用256M
        self.seeds = self.SEEDS[0: self.hash_counts]
        self.key = key
        self.hashfunc = []
        self.server = conn
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def is_exists(self, str_input):
        str_input = self.unicode_to_ascii(str_input)
        name = self.key + "_" + str(str_input[0] % self.block_num)
        if not str_input:
            return False
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()
        ret = True
        for f in self.hashfunc:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, str_input):
        str_input = self.unicode_to_ascii(str_input)
        name = self.key + "_" + str(str_input[0] % self.block_num)
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()

        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)

    def unicode_to_ascii(self, str_input):
        return str_input if self._version_check() else str_input.encode('ascii')

    def _version_check(self):
        return sys.version_info[0] == 2

    def get_status(self):
        bit_status = 'Bit位数: {}'.format(self.bit)
        hash_status = 'Hash次数: {}'.format(self.hash_counts)
        mem_status = '内存: {} M'.format(self.mem)
        block_status = 'Bit块数: {}\t\t\tInfo:每块512M'.format(self.block_num)
        return "\n".join([bit_status, hash_status, mem_status, block_status])


if __name__ == '__main__':
    """ 第一次运行时会显示 not exists!，之后再运行会显示 exists! """
    bf = BloomFilter(conn=conn)
    if bf.is_exists('http://www.baidu.com'):  # 判断字符串是否存在
        print('exists!')
    else:
        print('not exists!')
        bf.insert('http://www.baidu.com')
    bf.get_status()