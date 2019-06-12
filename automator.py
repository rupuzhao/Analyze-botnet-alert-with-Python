#import xml.etree.ElementTree as ET
import mysql.connector
from datetime import datetime, timedelta
import subprocess
import ipaddress

#parse xml file using substring to extract data


file = input('Enter the file name of  notice file(include path): ')

with open(file, "rt") as in_file:
    for line in in_file:
        if "<IP_Address>" in line:
            startindex = line.find('s>') + 2
            endindex = line.find('</')
            ip = line[startindex : endindex]
            # print("Post-NAT IP​: " + ip)
        if "<Port>" in line:
            startindex = line.find('t>') + 2
            endindex = line.find('</')
            port = line[startindex : endindex]
            # print("Post-NAT port​: " + port)
        if "<Destination_IP>" in line:
            startindex = line.find('P>') + 2
            endindex = line.find('</')
            rip = line[startindex : endindex]
            # print("Remote-IP​: " + rip)
        if "<Destination_Port>" in line:
            startindex = line.find('t>') + 2
            endindex = line.find('</')
            rport = line[startindex : endindex]
            # print("Remote port​: " + rport)
        if "<TimeStamp>" in line:
            startindex = line.find('p>') + 2
            endindex = line.find('</')
            timestamp = line[startindex : endindex]
            # print("Timestamp (in Zulu or UTC format)​: " + timestamp)

#use datetime and timedelta to convert string to time and change the time zone
datetimeUTC = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
datetime = datetimeUTC + timedelta(hours=-4)
hour = datetime.hour + 1
minute = datetime.minute
hour = str(hour)
datetimestr = datetime.strftime('%Y-%m-%d %H:%M:%SZ')
cTime = str(datetimestr[:-6])
print("local time(EDT): " + datetimestr)

if len(hour) == 1:
    hour = hour + '0'

nat_csv = 'nat.csv.20160321' + hour + '.csv.gz'
command = 'zgrep "' + cTime + '" /root/'+ nat_csv + ' | grep "' + ip +', '+ port +'"'
output = subprocess.check_output(command, shell=True)

list1 = []
list2 = []
if output is not None:
    line = output.split()
    for a in line:
        w = str(a).split(':')
        list1.append(w[1])
    for b in list1:
        time1 = int(b)
        time2 = int(str(minute))
        if time1 >= time2:
            list2.append(time1 - time2)
        else:
            list2.append(time2 - time1)

    parse = (str(line[list2.index(min(list2))])).split(",")
    preip = ipaddress.ip(parse[2])
    print("Pre-Nat IP: " + preip)

    try:
        cnx = mysql.connector.connect(user='root', password='toor', host='127.0.0.1', database='logs_db')
        commend1 = "select mac_string from dhcp where ip_decimal = '" + preip + "' and timestamp <= '" + datetimestr + "' order by timestamp desc;"
        cursor = cnx.cursor(buffered=True)
        cursor.execute(commend1)
        macaddress = cursor.fetchone()
    except mysql.connector.Error:
            print("Error")

    if macaddress == None:
        print("No Mac Address")
    else:
        print("Mac Address: " + macaddress)

    if "172.19." in parse[2]:
            try:
                cnx = mysql.connector.connect(user='root', password='toor', host = '127.0.0.1', database='logs_db')
                commend2 = "select distinct username from radacct where CallingStationId = '" + macaddress + "';"
                cursor = cnx.cursor(buffered=True)
                cursor.execute(commend2)
                user = cursor.fetchone()
            except mysql.connector.Error:
                print("Error")
    else:
        try:
            cnx = mysql.connector.connect(user='root', password='toor', host='127.0.0.1', database='logs_db')
            commend3 = "select distinct contact from contactinfo where mac_string = '" + macaddress + "';"
            cursor = cnx.cursor(buffered=True)
            cursor.execute(commend3)
            user = cursor.fetchone()
        except mysql.connector.Error:
            print("Error")

    if user == None:
        print("No User")
    else:
        print("User: " + user)











# print(datetimeETC2)
# with open("nat.csv.2016032017.csv") as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(" ".join(row[0]))

# search_for = [datetimeETC1]
# preip = ""
# macaddress = ""
# user = ""

#
# #identify the user with timestamp and his mac address
# with open('radius_logs.csv') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         if datetimeETC2 in row[0]:
#             if macaddress in row[2]:
#                 user = format(row[1])
#                 print("Username: " + user)

