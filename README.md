# ntp-python-stats
This Python program will monitor all NTP UDP traffic on port 123, it's very convenient for public NTP pool servers.
It generates staticstics into a MySQL (in-memory) database, from there the statistics are queried and sent to Graphite exporter
to store the metrics into Prometheus.

Requirements:
* Prometheus server
* Graphite Exporter
* Node Exporter
* Grafana
* MySQL
* Python 3+ (and PyMySQL)
* TCPdump (and the rights to run it, sudo for example)


The end-result in grafana will look like this:
![alt tag](https://github.com/HyperDevil/ntp-python-stats/blob/master/ntp.PNG?raw=true)
