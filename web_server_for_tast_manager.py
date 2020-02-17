#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
    ./dummy-web-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""
import os.path
import pickle
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import json
import sys

memory_path = "memory"


class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        get_msg = self.stringify(self.load())
        json_msg = json.dumps(get_msg)
        msg = bytes(json_msg.replace("[", "popsicles_r").replace("]", "popsicles_l").replace(
            "{", "[").replace("}", "]").replace("popsicles_r", "{").replace("popsicles_l", "}"), 'utf-8')
        print(msg)
        self.wfile.write(bytes(json_msg, 'utf-8'))

    @staticmethod
    def stringify(dic):
        string_construct = {}
        for k, v in dic.items():
            if len(v) > 0:
                string_construct[k.decode('utf-8')] = [[i[0].decode('utf-8'), i[1].decode(
                    'utf-8'), i[2].decode('utf-8'), i[3].decode('utf-8')] for i in v]
            else:
                string_construct[k.decode('utf-8')] = []
        return string_construct

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        content = self.rfile.read(int(self.headers['Content-Length']))
        post = dict(urllib.parse.parse_qs(content, keep_blank_values=1))
        action = post[b'action'][0]
        deadline = post[b'deadline'][0]
        index = post[b'index'][0]
        person = post[b'person'][0]
        task = post[b'task'][0]
        imp = post[b'importancy'][0]
        job = post[b'job'][0]
        print("Got POST: ", action, deadline, index, person, task, imp, job)
        if action == b"create":
            print("creating")
            self.create_task(deadline, person, task, imp, job)
        elif action == b"update":
            print("updating")
            self.update_task(deadline, index, person, task, imp, job)
        elif action == b"delete":
            print("deleting")
            self.delete_task(deadline, index)
        else:
            print("-------- unknown action --------")

        print("current: ", self.load())

    def create_task(self, when, who, what, imp, job):
        mem = self.load()
        mem[when].append([who, what, imp, job])
        self.save(mem)

    def delete_task(self, when, which):
        mem = self.load()
        del mem[when][int(which)]
        self.save(mem)

    def update_task(self, when, which, who, what, imp, job):
        mem = self.load()
        ind = int(which)
        if ind == 0:
            mem[when] = []
        mem[when].append([who, what, imp, job])
        for time in mem.keys():
            if time != when:
                for i in range(len(mem[time])):
                    if mem[time][i][1] == what:
                        del mem[time][i]
        self.save(mem)

    @staticmethod
    def load():
        open_file = open(memory_path, 'rb')
        mem = pickle.load(open_file)
        open_file.close()
        return mem

    @staticmethod
    def save(mem):
        open_file = open(memory_path, 'wb')
        pickle.dump(mem, open_file)
        open_file.close()


def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        httpd.socket.close()


if __name__ == "__main__":

    memory = {b"today": [], b"manana": [], b"eow": [], b"future": []}
    if not os.path.exists(memory_path):
        file_ob = open(memory_path, 'wb')
        pickle.dump(memory, file_ob)
        file_ob.close()
    run()
