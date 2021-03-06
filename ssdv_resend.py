#!/usr/bin/python3

import urllib.parse
import urllib.request
import json
from datetime import datetime, timedelta
import sys
import os.path
import time

def get_list_of_missing_packets(PayloadID, Minutes):
	result = ''
	
	time_limit = datetime.utcnow() - timedelta(0,Minutes*60)	# n minutes ago
	url = 'http://ssdv.habhub.org/api/v0/images?callsign=' + PayloadID + '&from=' + time_limit.strftime('%Y-%m-%dT%H:%M:%SZ') + '&missing_packets=true'

	print("url", url)
	
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as response:
		the_page = response.read()			# content = urllib.request.urlopen(url=url, data=data).read()
	# print(the_page)
			
	temp = the_page.decode('utf-8')
	j = json.loads(temp)
	# print(j)
	
	line = ""
	for index, item in enumerate(j):
		# only interested in latest 2 images
		if index >= (len(j) - 2):
			# only interested in images that have missing packets
			# if len(item['missing_packets']) > 0:
			# only interested in images that have missing packets or which are yet to be completed
			if len(item['missing_packets']) > 0 or (not item['received_eoi']):
				print(item['id'], item['image_id'], len(item['missing_packets']))
				print(item['missing_packets'])
				# pl = item['packets']
				# print("highest_packet_id = ", item['last_packet'])
				first_missing_packet = -1
				last_missing_packet = -1
				missing_packets = item['missing_packets'] + [9999]
				
				# Header for this image
				if line != "":
					line = line + ","
				line = line + str(item['image_id']) + ":" + str(item['last_packet']) + "="				
				image_line = ""
				
				for mp_index, mp in enumerate(missing_packets):
					if mp_index == 0:
						first_missing_packet = mp
						last_missing_packet = mp

					if (mp > (last_missing_packet+1)):	# or (mp_index == len(item['missing_packets'])-1):
						# emit section
						if image_line != "":
							image_line = image_line + ","
						if last_missing_packet == first_missing_packet:
							image_line = image_line + str(last_missing_packet)
						else:
							image_line = image_line + str(first_missing_packet) + "-" + str(last_missing_packet)
						first_missing_packet = mp
					
					last_missing_packet = mp
				line = line + image_line
				
	result = "!" + line

	return result

if len(sys.argv) <= 2:
	print ("Usage: ssdv_resend <payload_id> <gateway_callsign> [folder]\n")
	quit()

payload_id = sys.argv[1]

gw_callsign = sys.argv[2]
	
if len(sys.argv) >= 4:
	folder = sys.argv[3]
else:
	folder = './'
	
print('Payload Id = ' + payload_id)
print('Gateway Callsign = ' + gw_callsign)
print('Folder = ' + folder)

while True:
	# if os.path.isfile(folder + 'get_list.txt'):
	if (datetime.utcnow().second < 0) or (datetime.utcnow().second > 50):
		print("Checking ...")
		# os.remove(folder + 'get_list.txt')
		line = get_list_of_missing_packets(payload_id, 5)
		if len(line) <= 1:
			print("No missing packets:", line)
		else:
			print("Missing Packets:", line)
		with open(folder + 'uplink.txt', "w") as text_file:
			if line != '':
				line = line + ";" + gw_callsign + "\n"
				print(line, file=text_file)
		time.sleep(9)
	else:
		print('.',end="")
		sys.stdout.flush()
		time.sleep(1)

