from netmiko import ConnectHandler
import re
import socket
import getpass

show_int_list = []

hosts = ['fre-agg4.cenic.net', 'frg-agg4.cenic.net', 'lax-agg6.cenic.net', 'lax-agg7.cenic.net', 'oak-agg4.cenic.net',
         'riv-agg4.cenic.net', 'sac-agg4.cenic.net', 'sdg-agg4.cenic.net', 'svl-agg4.cenic.net', 'tri-agg2.cenic.net',
         'tus-agg3.cenic.net']

username = raw_input("Enter username: ")
password = getpass.getpass("Enter password: ")
print "\n"

for target_host in hosts:

    # Initialize interface counting variables
    tenG_count = 0
    oneG_count = 0

    # Perform DNS lookup of hosts to get IP for ConnectHandler function
    target_ip = socket.gethostbyname(target_host)

    cisco_asr9k = {
        'device_type': 'cisco_xr',
        'ip': target_ip,
        'username': username,
        'password': password
    }

    net_connect = ConnectHandler(**cisco_asr9k)
    output = net_connect.send_command("show interface description")

    # Print hostname as header for data
    print "Executing on host: %s" % target_host

    # Split interface output by newline
    show_int_lines = output.split('\n')

    for line in show_int_lines:

        # Skip first line header
        if 'Interface' in line:
            continue
        elif '--------------------------------------------------------------------------------' in line:
            continue

        # Break lines into clean words with a maximum of 3 splits to keep interface descriptions with spaces whole
        line_split = line.split(None, 3)

        # If interface has no description, the split above won't create fourth list item.
        # Append blank string for last item
        if len(line_split) == 3:
            line_split.append('')

        # Discard any lines that aren't the correct format
        if len(line_split) == 4:

            # Set variable names for each item in line for easier reference based on line index
            int_name, int_status, int_protocol, int_desc = line_split

            # Check if interface is down/admin-down and no description.
            if ((int_status == 'admin-down' or int_status == 'down') and
                    (int_protocol == 'admin-down' or int_protocol == 'down') and (int_desc == '')):

                # Match TenGigabitEthernet interfaces
                if re.match(r'Te', int_name):
                    tenG_count += 1

                # Match GigabitEthernet interfaces
                elif re.match(r'Gi', int_name):
                    oneG_count += 1

    # Append data to tupled list for later reference
    show_int_list.append((target_host, tenG_count, oneG_count))

# Sort final list
show_int_list.sort()

print "\n\n%-30s %-20s %-20s" % ('Hostname', '# of 10GE Ports', '# of 1GE Ports')

for item in show_int_list:
    print "%-30s %-20s %-20s" % (item[0], item[1], item[2])
