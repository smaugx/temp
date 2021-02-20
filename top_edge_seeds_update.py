#!/usr/bin/env python3
#! -*- coding:utf8 -*-

# -author:smaugx-

import os
import requests
import time
import json
import argparse

class EdgeManager(object):
    def __init__(self, outfile, host = ''):
        self.start_time_ = int(time.time())
        self.outfile_ = outfile  # save edge ip list as json file
        self.first_edge_ = host  # give a edge ip:port to update edge ip list
        self.edge_ip_port_list_ = list() # cache all edge ip:port
        self.tmp_outfile_ = "/tmp/.top_edge_list.json"  # load when start

        if not self.first_edge_:
            # load from tmp_outfile_
            if os.path.exists(self.tmp_outfile_):
                old_edge_list = json.loads(open(self.tmp_outfile_, 'r').read())
                for edge in old_edge_list:
                    if edge not in self.edge_ip_port_list_:
                        self.edge_ip_port_list_.append(edge)

            random_index = random.randint(0, len(self.edge_ip_port_list_) - 1)
            self.first_edge_ = self.edge_ip_port_list_[random_index]
        else:
            # do nothing
            None

    def get_edge_neighbors(self, ip_port):
        edge_list = []
        if not ip_port:
            return  edge_list

        url = "http://{0}/".format(ip_port)  # http://127.0.0.1:19081/
        mydata = "version=1.0&method=get_edge_neighbors"

        try:
            res = requests.post(url, data = mydata)
            if res.status_code == 200:
                result = res.text
                edge_list = json.loads(result)
                print("get edge_list from url:{0}", url)
                print(edge_list)
        except Exception as e:
            print("catch Exception:{0} from url:{1}", e, url)

        return edge_list

    def choose_edge(self):
        now = int(time.time())
        runing_time = now - self.start_time_
        if runing_time < 5 * 60 * 60:  # 5 hour
            return self.first_edge_

        random_index = random.randint(0, len(self.edge_ip_port_list_) - 1)
        return self.edge_ip_port_list_[random_index]

    def update_edge(self):
        ip_port = self.choose_edge()
        edge_list = self.get_edge_neighbors(ip_port)

        for edge in edge_list:
            if edge not in self.edge_ip_port_list_:
                self.edge_ip_port_list_.append(edge)
                print("update cache edge_ip_port_list_:{0}, total size:{1}".format(edge, len(self.edge_ip_port_list_)))

        return


    def dump_edge_list(self):
        if not self.edge_ip_port_list_:
            return
        with open(self.outfile_, 'w') as fout: # overwrite
            fout.write(json.dumps(self.edge_ip_port_list_))
            print("dump edge_ip_port_list:{0} to file:{1}".format(len(self.edge_ip_port_list_), self.outfile_))
            fout.close()
        return

    def run(self):
        while True:
            print("EdgeManager alive")
            self.update_edge()
            self.dump_edge_list()
            time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='EdgeSeedsManager -- 管理和维护 TOP Chain Edge IP 列表'
    parser.add_argument('-o', '--outfile', help="save edge ip list to this file, eg: /tmp/top_edge_seeds.json", default='/tmp/top_edge_seeds.json')
    parser.add_argument('-e', '--edge_host', help='the first edge to connect, eg: 127.0.0.1:19081', required=True)
    args = parser.parse_args()

    outfile = args.outfile
    host    = args.edge_host


    print("EdgeManager started")
    edge_manager = EdgeManager(outfile, host)
    edge_manager.run()
