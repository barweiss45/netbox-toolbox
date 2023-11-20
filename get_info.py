#!/usr/bin/env python

__version__ = "1.0.4"
__author__ = "Kevin Brown"

# Import required modules
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from pynetbox import api

# Load environment variables from the .env file
dotenv_path = "var/.env"
load_dotenv(dotenv_path)

'''
API
'''

# Read the URL and API token from the environment variables
netbox_url = os.getenv("NETBOX_API_URL")
api_token = os.getenv("NETBOX_API_TOKEN")

# Connect to the NetBox API
nb = api(url=netbox_url, token=api_token, threading=True)

'''
USER INPUT
'''

# Prompt the user for the information they would like to see
print("What information would you like to see?")
print("1 - All Devices")
print("2 - All Interfaces")
print("3 - Interfaces on a specifc Device")
print("4 - Devices in a specific Rack")

# Collect the user input
try:
    user_entry = int(input("Enter one of the numbers from above:\n"))
    
    if user_entry == 1:
        user_target = "Devices"
        print("---\nExecuting API calls and collecting responses. This may take a moment...")
        user_query = nb.dcim.devices.all()
        output_suffix = "Devices_All"
    elif user_entry == 2:
        user_target = "Interfaces"
        print("---\nExecuting API calls and collecting responses. This may take a moment...")
        user_query = nb.dcim.interfaces.all()
        output_suffix = "Interfaces_All"
    elif user_entry == 3:
        user_target = "Interfaces"
        device_id = int(input("\nWhat is the Device ID?\n"))
        
        # Get the device name for the provided device id
        device_name = nb.dcim.devices.get(id=device_id)
        
        # Break if there is no entry for the provided device id
        if device_name == None:
            print("\nThe provided Device ID does not have an entry. Please provide a valid Device ID.")
            exit()
        
        print(f"---\nQuerying Device ID {device_id} > > > > {device_name} ...")
        
        # API call for interfaces with a filter based on the device name
        user_query = nb.dcim.interfaces.filter(device=device_name)

        output_suffix = f"Interfaces_{device_name}"
    elif user_entry == 4:
        user_target = "Devices"
        rack_name = input("\nWhat is the Rack Name?\n")
        
        # Retrieve the rack by name
        rack = nb.dcim.racks.get(name=rack_name)
        
        # Break if there is no entry for the provided device id
        if rack == None:
            print("\nThe provided Rack Name does not have an entry. Please provide a valid Rack Name.")
            exit()
        
        print(f"---\nQuerying Devices in Rack {rack} ...")
        
        # API call for interfaces with a filter based on the device name
        user_query = nb.dcim.devices.filter(rack_id=rack.id)

        output_suffix = f"Devices_Rack_{rack_name}"
    else:
        print("\nInvalid input. Please enter a valid number.")
        exit()

except ValueError:
    print("\nInvalid input. Please enter a valid number.")
    exit()

'''
Output
'''

# Retrieve the current date and time
current_date = datetime.now().strftime("%Y.%m.%d")

# Construct the output path and filename
output = f"output/{current_date}-{output_suffix}.csv"

# Open the CSV file for writing
with open(output, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write the data for Devices
    if user_target == "Devices":
        csv_writer.writerow(["rack","position","name","device_type","primary_ip","id","url"])
        for query_reply in user_query:
            csv_writer.writerow([query_reply.rack, query_reply.position, query_reply.name, query_reply.device_type, query_reply.primary_ip, query_reply.id, query_reply.url])
    
    # Write the data for Interfaces
    elif user_target == "Interfaces":
        csv_writer.writerow(["device","name","id","url"])
        for query_reply in user_query:
            csv_writer.writerow([query_reply.device, query_reply.name, query_reply.id, query_reply.url])
    
# Confirm that the script is complete and the output has been written
print(f"\nComplete!\nAPI Reponse has been written to /{output}")

# End
