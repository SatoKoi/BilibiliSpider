# -*- coding:utf-8 -*-
import requests
from scrapy.selector import Selector
import pymysql

headers = {
    "Host": "www.xicidaili.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.360",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}

def crawl_ips():
    """从西刺网爬取ip代理"""
    response = requests.get("http://www.xicidaili.com/nn", headers=headers)
    selector = Selector(text=response.text)
    last_page = selector.css(".pagination a::text").extract()[-2]
    ip_list = []
    for ip_page in range(1, int(last_page)+1):
        if ip_page != 1:
            response = requests.get("http://www.xicidaili.com/nn/{0}".format(ip_page), headers=headers)
            selector = Selector(text=response.text)
        all_trs = selector.css("#ip_list tr")
        for tr in all_trs[1:]:
            speed = tr.css(".bar::attr(title)").extract_first(None)
            if speed:
                speed = float(speed.split('秒')[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append((ip, port, proxy_type, speed))
        for ip_info in ip_list:
            cursor.execute("""
                insert into ippool (ip, port, speed, proxy_type) VALUES (%s, %s, %s, %s)
                on duplicate KEY update 
                speed=VALUES (speed), 
                proxy_type=VALUES (proxy_type)
            """, (ip_info[0], ip_info[1], ip_info[3], ip_info[2]))
            conn.commit()


class GetIp(object):
    """从数据库里获取随机ip"""
    def __init__(self, cursor):
        self.cursor = cursor
    
    def _judge_ip(self, *mess):
        """判断ip地址是否可用"""
        ip, port, http = mess
        http_url = 'https://www.bilibili.com'
        proxy_url = "{0}://{1}:{2}".format(http.lower(), ip, port)
        proxy_dict = {
            "{}".format(http.lower()): proxy_url
        }
        try:
            response = requests.get(http_url, proxies=proxy_dict, timeout=5)
            # print(response)
        except Exception:
            print('invalid ip address and port {}'.format(proxy_url))
            self._delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 302:
                print('effective proxy {}'.format(proxy_url))
                return True
            else:
                print('invalid ip address and port {}'.format(proxy_url))
                self._delete_ip(ip)
                return False

    def get_random_ip(self):
        """获取随机ip"""
        random_sql = """
            select ip, port, proxy_type from ippool
            ORDER BY rand()
            limit 1
        """
        res = self.cursor.execute(random_sql)
        for ip_info in self.cursor.fetchall():
            if self._judge_ip(*ip_info):
                return "{}://{}:{}".format(ip_info[-1].lower(), ip_info[0], ip_info[1])
            else:
                return self.get_random_ip()

    def _delete_ip(self, ip):
        self.cursor.execute("delete from ippool where ip='%s'" % ip)
        return True


if __name__ == '__main__':
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='123456',
        db='learning',
        charset='utf8'
    )

    cursor = conn.cursor()
    # crawl_ips()
    get_ip = GetIp(cursor)
    ip_proxy = get_ip.get_random_ip()
    print(ip_proxy)