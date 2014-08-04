#!/usr/bin/python 
# Who's Attacking Me Now? (WAMN)
# An application to parse ssh logs, report and map attacks on Debian based systems.
# Further functionality for other OSs and different logs will be added.
# WAMN is released under the GPL V2
# However we would like you to buy us pizza and beer if you like it!
# The authors accept no responsibility for damage cause by the program or irresponsible use
# Authors: Paul Mason (Paulmason126[at]gmail[dot]com) ; Kyle Fleming (kylefleming[at]gmail[dot}com)
# Contributors: TBC Come on folks!!!
# Thanks: TJ O'Connor Author of Violent Python which gave us the inspiration for this app


import sys, signal, socket
import urllib2
import urlparse 
import re 
import pygmaps
import pygeoip 
import mechanize
import os
from logsparser.lognormalizer import LogNormalizer as LN
from time import sleep
os.system('clear')
normalizer = LN('/usr/local/share/logsparser/normalizers')
gi = pygeoip.GeoIP('./GeoLiteCity.dat')
countries = {}
latlong = {}

def geo_menu():
  print 'Geolocation Menu'
  print '1) Enter and locate an IP Addr'
  print '2) Enter a url, resolve IP and geolocate'
  print '3) Log Check and IP geolocate (sshd)'
  print '0) Exit'
  geo_option = raw_input('Please choose an option: ')
  try:
    choice = geomenudict[geo_option]
    choice()
  except KeyError:
    print "try again..."
    geo_menu()
 
def logcheck():
  LOG = './auth.log'
  auth_logs = open(LOG, 'r')
  attacks = {}
  users = {}
  origin_unknown = {}
  print "Parsing log file"
  for log in auth_logs:
    l = {"raw": log }
    normalizer.normalize(l)
    if l.get('action') == 'fail' and l.get('program') == 'sshd':	
      u = l['user']
      p = l['source_ip']
      oct1, oct2, oct3, oct4 = [int(i) for i in p.split('.')] #split IP so we can check for private addr
      if oct1 == 192 and oct2 == 168 or oct1 == 172 and oct2 in range(16, 32) or oct1 == 10: #check for private addr
        print "Private ip attack, %s No geolocation available" % str(p)
      if attacks.has_key(p): #if not private do geolocate
        attacks[l['source_ip']] = attacks.get(l['source_ip'], 0)+ 1
        countryRecord(p)
      else:
        printRecord(p)
        attacks[l['source_ip']] = attacks.get(l['source_ip'], 0)+ 1
      users[u] = users.get(u, 0)+ 1  	
  sort(attacks, users)
  gmaps()
  en2con()
  main()

# reads takes ip addr as string. Reads .dat file, prints coresponding lat, long and area of ip
def geo_ip():
  print "Enter IP address"
  ipaddr = raw_input("Please enter an IP Address: ")
  printRecord(ipaddr) 
  gmaps()

def countryRecord(p):
  # This function gets run just to keep the country attack count right if the IP address doesn't need geolocated again.
  # This needs fixed (As in removed, there must be a nicer way to do it!)
  rec = gi.record_by_name(p)
  try:
    country = rec['country_name']
    if country:
      countries[rec['country_name']] = countries.get(rec['country_name'], 0)+ 1
  except TypeError:
    print "No country in DB"
  return

def printRecord(tgt):
  rec = gi.record_by_name(tgt)
  try:
    city = rec['city']
  except TypeError:
    print "no city in DB"
  try:
    region = rec['time_zone']
  except TypeError:
    print "no timezone in db"
  try:
    country = rec['country_name']
    if country:
      countries[rec['country_name']] = countries.get(rec['country_name'], 0) + 1
	
  except TypeError:
    print "No country in db"
  try:
    long = rec['longitude']
    lat = rec['latitude']
    if lat and long:
      latlong[rec['latitude']] = rec['longitude']		
  except TypeError:
    print "No coords in db"
  try:
    print '[*] Target: ' + tgt + ' Geo-located. '
    print '[+] ' + str(city) +', '+str(region)+ ', '+ str(country)
    print '[+] Latitude: '+str(lat)+ ', ' +str(long)
    print ''
  except UnboundLocalError:
    print "error"
  return

#  en2con()
 # main()

def gmaps():
  map = pygmaps.maps(55.9013, -3.536, 3)
  for p,k in latlong.items():
    map.addpoint(float(p), float(k))
  map.draw('./map.html')

def sort(attacks, users):
  print "Attack IP Sorted in order"	
  for i,j in sorted(attacks.items(), cmp = lambda a,b: cmp(a[1], b[1]) ):
    #print "Attack IP sorted in order"
    print "\t%s (%i attempts)" % (i,j)
    
  print "Attacking countries Sorted in order"
  for p,k in sorted(countries.items(), cmp = lambda c,d: cmp(c[1], d[1]) ):
   # print "Attacking countries sorted in order"
    print "\t%s (%i attempts)" % (p,k)
  print "Usernames used in attacks Sorted in Order"
  for u,a in sorted(users.items(), cmp = lambda e,f: cmp(e[1], f[1]) ):
    print "\t%s (%i attempts)" % (u,a)

def resolvegeoip():
  ur = raw_input("URL [>] ")
  if "http://" in ur or "https://" in ur:
    req = urllib2.Request(ur)
  else:
    url = "http://" + ur
    req = urllib2.Request(url)
  webdat = urllib2.urlopen(req)
  ip = socket.gethostbyname(urlparse.urlparse(webdat.geturl()).hostname)
  print ip
  printRecord(ip)
  gmaps()
  en2con()
  main()

def ctrlc_catch(signal, frame):

  print "\n Exiting clean"
  sys.exit(0)

def en2con(Prompt='Hit Enter to continue'):
	raw_input("Hit Enter to continue")
	
def main():
  signal.signal(signal.SIGINT, ctrlc_catch)
  print 'Welcome to WAMN.' 
  print '1) Automatic set-up and run on local system' 
  print '2) Set advanced options' 
  print '3) Perform specific task from WAMN toolkit.' 
  print '0) Exit'
  option = raw_input('Please choose an option: ') 
  try:
    main_choice = main_menu[option]
    main_choice()
  except KeyError:
    print "Invalid selection"
    main()
	
def toolsmenu(): 
  print 'Tools Main Menu'
  print '1) Geolocation Tool'
  print '2) TBC'
  print '3) TBC'
  print '0) Exit'
  tools_option = raw_input('Please choose an option: ')
  try:
    choice = tools_dict[tools_option]
    choice()
  except KeyError:
    print "Invalid selection"
    toolsmenu()
	
main_menu = {
  '2': geo_ip,
# '2': tbc1,
  '3': toolsmenu,
  '0': exit
  }
tools_dict = {
  '1': geo_menu,
# '2': tbc,
# '3': tbc,
  '0': exit
  }
geomenudict = {
  '1': geo_ip,
  '2': resolvegeoip,
  '3': logcheck,
  '0': exit
  }
main()
