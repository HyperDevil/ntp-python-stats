#!/usr/bin/python3

import subprocess
import pymysql
import socket
import struct
import time
from threading import Thread

# Running this script as root is dangerous, someone with write access to this file can do bad things!!!
# This is advised:
# sudo groupadd pcap
# sudo usermod -a -G pcap $USER
# sudo chgrp pcap /usr/sbin/tcpdump
# sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
# sudo ln -s /usr/sbin/tcpdump /usr/bin/tcpdump


#Database layout (memory database)
#CREATE TABLE `clients` (
#  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
#  `ip` int(10) UNSIGNED NOT NULL,
#  `version` int(1) NOT NULL
#) ENGINE=MEMORY DEFAULT CHARSET=latin1;
#ALTER TABLE `clients`
#  ADD UNIQUE KEY `ip` (`ip`),
#  ADD KEY `time` (`time`),
#  ADD KEY `version` (`version`);

def getdata():
  #connect to database, remember credentials and hostname and database
  db = pymysql.connect(host='localhost',user='bla',passwd='bla',db='ntp',autocommit=True)
  cursor = db.cursor()
  #start the tcpdump process (-n no reverse lookup)
  p = subprocess.Popen(('sudo', 'tcpdump', 'dst', 'port', '123', '-n', '-l'), stdout=subprocess.PIPE)

  while True:
    for row in iter(p.stdout.readline, b''):
      data = str(row.rstrip())
      #split output into list
      splitted = data.split()

      #sometimes something weird happens, therefor test the output
      try:
        type = splitted[6][:-1]
      except IndexError:
       pass

      #get the values we want
      sourceipsplit = splitted[2].split('.',4)
      sourceip = ".".join(sourceipsplit[0:-1])
      destinationip =splitted[4][:-1]
      protocolversion = splitted[5][:-1]

      #we are only interested in the client traffic
      if type == 'Client':
        ip = sourceip

        #parse this into integers for MySQL
        if 'NTP' not in protocolversion:
          protocolversion = 0
        elif protocolversion == 'NTPv1':
          protocolversion = 1
        elif protocolversion == 'NTPv2':
          protocolversion = 2
        elif protocolversion == 'NTPv3':
          protocolversion = 3
        elif protocolversion == 'NTPv4':
          protocolversion = 4
        #construct SQL and replace (delete if exist and insert new)
        sql = """REPLACE INTO clients(time,ip,version) VALUES (now(),%s,%s)"""
        sqlip = struct.unpack("!I", socket.inet_aton(ip))[0]
        try:
          cursor.execute(sql, (sqlip, protocolversion))
          #for debug: print(cursor._last_executed)
        except pymysql.Error as e:
          print("SQL Error %d: %s" %(e.args[0], e.args[1]))

def netcat(host, port, content):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect((host,int(port)))
  s.send(content.encode('utf-8'))
  s.close()

def exporter():
  #connect to database, remember credentials and hostname and database
  db = pymysql.connect(host='localhost',user='bla',passwd='bla',db='ntp',autocommit=True)
  cursor = db.cursor()
  while True:
    #get data from MySQL
    sql = "SELECT count(*) AS count, version FROM ntp.clients WHERE time > NOW() - INTERVAL 1 MINUTE GROUP BY version"
    cursor.execute(sql)
    ntpstats = cursor.fetchall()
    for row in ntpstats:
      #define your hostname here, and remember graphite exporter mapping
      promstring = "ntpserver.<servername>." + "" + str(row[1]) + " " + str(row[0]) + " "+ str(int(time.time()))
      #send data to graphite exporter on localhost
      netcat('localhost',9109,promstring)

    #automatically delete records older then 30 minutes
    delsql="DELETE FROM clients WHERE time < (NOW() - INTERVAL 30 MINUTE)"
    try:
      cursor.execute(delsql)
    except pymysql.Error as e:
      print("SQL Error %d: %s" %(e.args[0], e.args[1]))

    #sleep for 30 seconds
    time.sleep(30)

#multi-thread these functions
if __name__ == '__main__':
  Thread(target = getdata).start()
  Thread(target = exporter).start()
