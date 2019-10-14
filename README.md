# ntp-python-stats
This Python program will monitor all NTP UDP traffic on port 123, it's very convenient for public NTP pool servers.
It generates statistics into a MySQL (in-memory) database, from there the statistics are queried and sent to Graphite exporter
to store the metrics into Prometheus.  
Statistics gathered: NTP version of client, IP of client, last-time-seen client.  
The MySQL in-memory database is cleared every 30 minutes (to save space), it's also in-memory because the I/O load is pretty high. (aprox 80 QPS with 3500 clients)  

Requirements:
* A working Prometheus server
* Working Graphite Exporter
* Working Node Exporter
* Working Grafana 
* Working MySQL server
* Python 3+ (and PyMySQL)
* TCPdump (and the rights to run it, sudo for example)

Files
* ntp-dashboard.json (grafana dashboard) remember to change source and server name in queries
* ntp.sql (SQL dump of database structure) create database ntp and make a user for that DB with insert, update and delete rights

The end-result in grafana will look like this:
![alt tag](https://github.com/HyperDevil/ntp-python-stats/blob/master/ntp.PNG?raw=true)
