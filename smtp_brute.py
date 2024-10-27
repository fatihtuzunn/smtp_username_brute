#!/usr/bin/env python3
#
# This script tests if users exist on an SMTP server using the MAIL FROM command.
#

import socket
import sys
import time

def connect_to_smtp(ip_address):
    """Establish a connection to the SMTP server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, 25))
        banner = s.recv(1024).decode()
        print(f"Connected to SMTP server: {banner}")
        return s
    except socket.error as e:
        print(f"Socket error while connecting: {e}")
        return None

def check_user(s, user):
    """Check if a user exists on the SMTP server using the MAIL FROM command."""
    try:
        # Use a generic sender email that is unlikely to exist
        sender = "test@example.com"
        s.sendall(f'MAIL FROM:<{sender}>\r\n'.encode())
        response = s.recv(1024).decode()
        
        # Send the RCPT TO command for the user we are checking
        s.sendall(f'RCPT TO:<{user}>\r\n'.encode())
        response = s.recv(1024).decode()
        return response
    except socket.error as e:
        print(f"Socket error while checking user '{user}': {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <ip> <username wordlist>")
        print(f"Example: {sys.argv[0]} 192.168.1.108 usernames.txt")
        sys.exit(1)

    ip_address = sys.argv[1]
    username_file = sys.argv[2]

    with open(username_file, 'r') as file:
        users = [user.strip() for user in file if user.strip()]

    for user in users:
        # Connect to the SMTP server
        smtp_socket = connect_to_smtp(ip_address)
        if not smtp_socket:
            print("Unable to connect to SMTP server. Exiting.")
            sys.exit(1)

        response = check_user(smtp_socket, user)
        if response:
            print(f"Checking user: {user} - Response: {response.strip()}")
            # Check for common SMTP response codes
            if "250" in response:  # 250 usually means the user exists
                print(f"User exists: {user}")
            elif "550" in response:  # 550 usually means the user does not exist
                print(f"User does not exist: {user}")
            else:
                print(f"Unexpected response for {user}: {response.strip()}")
        else:
            print(f"Failed to check user: {user}")

        # Close the SMTP socket
        smtp_socket.close()

        # Wait a bit before the next request to avoid rate limiting
        time.sleep(1)

    print("Search finished!")

if __name__ == "__main__":
    main()
