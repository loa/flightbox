#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import web

filename = "transformation/pcasconf.ini"

urls = (
  '/', 'Index'
)

app = web.application(urls, globals())

render = web.template.render('templates/')

class Index(object):
    def GET(self):
        return render.form()

    def POST(self):
        form = web.input(name="Nobody", greet="Hello")
        greeting = "%s, %s, %s" % (form.tail, form.ICAO, form.maxrange)
        flightID = "my_Tail: '%s'" % (form.tail)
        flightICAO = "my_ICAO: '%s'" % (form.ICAO)
        maxrangeNM = "my_Range: '%s'" % (form.maxrange)
        target = open(filename, 'w')
        target.truncate()
        target.write("[DEFAULT]")
        target.write("\n")
        target.write(flightID)
        target.write("\n")
        target.write(flightICAO)
        target.write("\n")        
        target.write(maxrangeNM)
        target.write("\n")
        target.close()
        return render.index(greeting = greeting)
    
if __name__ == "__main__":
    app.run()

