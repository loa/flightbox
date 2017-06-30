#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import web
from web import form
import time
import os

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
        s = web.input(FLARM = [])

        if s.submit == 'FLARM' and s.flarm == '2':
            os.system("sudo service rtlsdr-ogn stop")
            
        elif s.submit == 'FLARM' and s.flarm == '1':
            os.system("sudo service rtlsdr-ogn restart")
        
        else:
        
            #form = web.input(name="Nobody", greet="Hello")
            form = web.input() 
            #greeting = "%s, %s, %s" % (form.ICAO,form.modecsep,form.modecdet)

            flightICAO = "my_ICAO: %s" % (form.ICAO)
            flightMODECsep = "modec_sep: %s" % (form.modecsep)
            flightMODECdet = "modec_det: %s" % (form.modecdet)
            
            target = open(filename, 'w')
            target.truncate()
            target.write("[DEFAULT]")
            target.write("\n")
            target.write(flightICAO)
            target.write("\n")        
            target.write(flightMODECsep)
            target.write("\n")
            target.write(flightMODECdet)
            target.write("\n")
            target.close()
                    
            for i in range(1,10):
               print 'REBOOT',i
               #Do your code here
               time.sleep(1)
               os.system("sudo reboot")
		   
    
if __name__ == "__main__":
    app.run()

