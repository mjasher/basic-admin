import tornado.ioloop
import tornado.web
import os
import sqlite3
import json

class StaticView(tornado.web.RequestHandler):
    def get(self, path):
        path = os.path.join(os.path.dirname(__file__), 'static', path) 
        f = open(path, 'r')
        self.write(f.read())
        f.close()

class ClientsView(tornado.web.RequestHandler):
    def get(self):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("SELECT rowid, name, dob, email FROM clients")
        rows = c.fetchall()
        c.close()
        conn.close()
        # self.response.write(json.dumps(rows))
        dict_rows = [dict(zip(["rowid", "name", "dob", "email"], row)) for row in rows]
        self.write(json.dumps(dict_rows))

class ClientView(tornado.web.RequestHandler):
    # get a given row
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
    def put(self):
        data = json.loads(self.request.body)
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute("UPDATE clients SET name=?, dob=?, email=? WHERE rowid=?", (data["name"], data["dob"], data["email"], data["rowid"]))
        conn.commit()
        c.close()
        conn.close()
        self.write("{}")

    # delete a given row
    def delete(self):
        data = json.loads(self.request.body)
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
