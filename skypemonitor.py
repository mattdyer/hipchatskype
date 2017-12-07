import sys
import subprocess
import requests
import json
import time

if len(sys.argv) >= 3:
	mention_name = sys.argv[1]
	hipchat_token = sys.argv[2]
	
	if len(sys.argv) == 4:
		data_usage_threshold = int(sys.argv[3])
	else:
		data_usage_threshold = 2000
	
	print(data_usage_threshold)
	
	def on_skype_call():

		nettopArguments = ["nettop", "-P", "-m", "udp", "-p", "Skype Helper", "-l", "2", "-k", "tx_win,tc_class,interface,state,tc_mgt,cc_algo,time,rx_dupe,rx_ooo,rtt_avg,rcvsize,re-tx,P,C,R,W,bytes_out", "-x", "-d"]

		result = subprocess.check_output(nettopArguments)
		
		lines = result.splitlines()
		
		if len(lines) >= 4:
			bytes_in_value = lines[3].split()[2]

			if int(bytes_in_value) > data_usage_threshold:
				call_status = "On Call"
				
			else:
				call_status = "Available"
			
			print(bytes_in_value)
		else:
			print(0)
			call_status = "Available"
		
		return call_status

	def update_hipchat_status(new_status, status_message, mention_name, token):  # dnd or chat

		user_url = "https://api.hipchat.com/v2/user/@" + mention_name
		
		get_result = requests.get(user_url, params={"auth_token": token})
		
		print(get_result.status_code)
		
		if get_result.status_code == 200:
			try:
				user_data = json.loads(get_result.content)
				
				user_data["presence"]["show"] = new_status
				
				user_data["presence"]["status"] = status_message
				
				
				put_result = requests.put(user_url, params={"auth_token": token}, json=user_data)

				print(put_result.content)
				
			except TypeError:
				print('Error setting hipchat status')

	last_skype_result = "Available"

	while True:
		
		time.sleep(5)
		
		skype_result = on_skype_call()
		
		if skype_result != last_skype_result:
		
			print(skype_result)

			if skype_result == "On Call":
				update_hipchat_status("dnd", skype_result, mention_name, hipchat_token)
			else:
				update_hipchat_status("chat", skype_result, mention_name, hipchat_token)
		
		last_skype_result = skype_result

else:
	print("usage: python skypemonitor.py [mention_name] [token] [data_usage_threshold (optional)]")
