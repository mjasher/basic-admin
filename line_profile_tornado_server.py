# thanks to https://zapier.com/engineering/profiling-python-boss/

try:
    from line_profiler import LineProfiler

    def do_profile(follow=[]):
        def inner(func):
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)
                    for f in follow:
                        profiler.add_function(f)
                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    profiler.print_stats()
            return profiled_func
        return inner

except ImportError:
    def do_profile(follow=[]):
        "Helpful if you accidentally leave in production!"
        def inner(func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return inner

def get_number():
    for x in range(5000000):
        yield x

# @do_profile(follow=[get_number])
# def expensive_function():
#     for x in get_number():
#         i = x ^ x ^ x
#     return 'some result!'

# result = expensive_function()
# print(result)


import tornado.ioloop
import tornado.web
import tornado.escape
import os
import sqlite3
import json


# in production one would not connect to DB each time, but would have a pool of connections (eg. http://initd.org/psycopg/docs/pool.html)

class StaticView(tornado.web.RequestHandler):
    @do_profile(follow=[get_number])
    def get(self, path):
        path = os.path.join(os.path.dirname(__file__), 'static', path) 
        f = open(path, 'r')
        self.write(f.read())
        f.close()

class ClientsView(tornado.web.RequestHandler):
    @do_profile(follow=[get_number])
    def get(self):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("SELECT rowid, name, dob, email FROM clients")
        rows = c.fetchall()
        c.close()
        conn.close()
        dict_rows = [dict(zip(["rowid", "name", "dob", "email"], row)) for row in rows]
        self.write(json.dumps(dict_rows))

class ClientView(tornado.web.RequestHandler):
    # get a given row
    @do_profile(follow=[get_number])
    def get(self):
        rowid = self.get_argument('rowid')
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("SELECT rowid, name, dob, email FROM clients where rowid=?", (rowid,))
        rows = c.fetchall()
        c.close()
        conn.close()
        dict_rows = [dict(zip(["rowid", "name", "dob", "email"], row)) for row in rows]
        self.write(json.dumps(dict_rows))

    # create a new empty row, return id
    @do_profile(follow=[get_number])
    def post(self):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("INSERT INTO clients VALUES (?, ?, ?)", ("", "", ""))
        conn.commit()
        lastrowid = c.lastrowid
        c.close()
        conn.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"lastrowid": lastrowid}))

    # edit a given row
    @do_profile(follow=[get_number])
    def put(self):
        data = json.loads(tornado.escape.to_basestring(self.request.body))
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("UPDATE clients SET name=?, dob=?, email=? WHERE rowid=?", (data["name"], data["dob"], data["email"], data["rowid"]))
        conn.commit()
        c.close()
        conn.close()
        self.write("{}")

    # delete a given row
    @do_profile(follow=[get_number])
    def delete(self):
        data = json.loads(tornado.escape.to_basestring(self.request.body))
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("DELETE FROM clients WHERE rowid=?", (data["rowid"],))
        conn.commit()
        c.close()
        conn.close()
        self.write("{}")

app = tornado.web.Application([
    (r'/static/(.+)', StaticView), # all static files (html, css, js, images, etc.)
    (r'/api/clients', ClientsView), # get all clients 
    (r'/api/client', ClientView), # get, create/post, edit/put, delete a client
    # (r'/api/client/(.+)', ClientView), #  eg. /api/client/1 would call get(self, id) with id=1
], debug=True)


if __name__ == '__main__':
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
