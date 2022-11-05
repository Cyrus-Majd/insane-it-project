import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print ("Here is the", tag)
    print ("\"\"\"")
    print (value)
    print ("\"\"\"")
    print ()

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)


# TODO: put your application logic here!
# Read login credentials for all the users
# Read secret data of all the users

# STAGE 3
valid_logins = {}
def populate_valid_logins():
    with open("passwords.txt", "r") as fp:
        line = fp.readlines()
        for each in line:
            valid_logins[each.split()[0]] = each.split()[1]
        print("All valid logons:\n", valid_logins)
populate_valid_logins()

valid_secrets = {}
def populate_valid_secrets():
    with open("secrets.txt", "r") as fp:
        line = fp.readlines()
        for each in line:
            valid_secrets[each.split()[0]] = each.split()[1]
        print("All valid secrets:\n", valid_secrets)
populate_valid_secrets()

valid_cookies = {}
def set_cookies(usr, cookie):
    valid_cookies[usr] = cookie

def cookie_exists(cookie):
    for each in valid_cookies:
        print(each + " " + str(valid_cookies[each]))
        if (str(cookie).strip() == str(valid_cookies[each]).strip()):
            print("Cookie match found!")
            return ("y", each)
        # print("is ")
        # print(cookie)
        # print(" EQUAL to " + str(valid_cookies[each]))
    return ("n", "meh")

### Loop to accept incoming HTTP connections and respond.
tmp = success_page
while True:
    success_page = tmp
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print("================================")
    print("REQUEST TYPE: " + headers[0:headers.find("/") - 1] + ".")
    print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions

    # STAGE 4
    # Verify request type + invalid login format
    login_success = False
    if (headers[0:headers.find("/") - 1] == "POST"):
        print("====================BODY!!!!!!: " + body)
        print("====================HEADER!!!!!!: " + str(headers[headers.find("Cookie:") + 14:headers.find("Content") - 1]))
        print("====================HEAD BODY!!!!!!: " + str(header_body))
        if (body == "action=logout"): # case F
            print("logging out!")
            headers_to_send = 'Set-Cookie: token=' + "ur_mom" + '\r\n'
            html_content_to_send = login_page
        # check if cookies poggers
        elif (headers.find("Cookie:") != -1 and headers.find("Content") != -1 and len(str(headers[headers.find("Cookie:") + 14:headers.find("Content") - 1])) > 0):
            cookie = str(headers[headers.find("Cookie:") + 14:headers.find("Content") - 1])
            print("old thing" + cookie)
            print("GOING THROUGH ALL VALID COOKIES:")
            if (cookie_exists(cookie)[0] == "y"): # case C
                matchedUser = cookie_exists(cookie)[1]
                print("GOOD COOKIE")
                success_page = success_page + valid_secrets[matchedUser]
                html_content_to_send = success_page
                login_success = True
                headers_to_send = "Set-Cookie: token=" + str(cookie) + "\r\n"
            elif (cookie_exists(cookie)[0] == "n"): # case D
                print("ERROR, BAD COOKIE")
                html_content_to_send = bad_creds_page
                headers_to_send = "Set-Cookie: token=" + str(cookie) + "\r\n"
        # moving on to case E
        elif (body.find("username=") == -1 or body.find("password=") == -1 or len(body[body.find("username=") + 9:body.find("password=") - 1]) < 1 or len(body[body.find("password=") + 9:]) < 1):
            print("ERROR")
            html_content_to_send = bad_creds_page
        else:
            print(body[body.find("username=") + 9:body.find("password=") - 1])
            print(body[body.find("password=") + 9:])
            # case A
            if (valid_logins.has_key(body[body.find("username=") + 9:body.find("password=") - 1]) and valid_logins[body[body.find("username=") + 9:body.find("password=") - 1]] == body[body.find("password=") + 9:]):
                print("GOOD CREDS")
                success_page = success_page + valid_secrets[body[body.find("username=") + 9:body.find("password=") - 1]]
                html_content_to_send = success_page
                login_success = True
                rand_val = random.getrandbits(64)
                set_cookies(body[body.find("username=") + 9:body.find("password=") - 1], rand_val)
                print(rand_val)
                print("============================ COOKIES ARE NOW: " + str(valid_cookies[body[body.find("username=") + 9:body.find("password=") - 1]]))
                headers_to_send = "Set-Cookie: token=" + str(rand_val) + "\r\n"
            else: # case B
                print("BAD CREDS")
                html_content_to_send = bad_creds_page
    elif (headers[0:headers.find("/") - 1] == "GET"):
        headers_to_send = ''
        html_content_to_send = login_form
            


    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    # THE CHEESE??? =============================# html_content_to_send = login_page
    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    # THE CHEESE PART TWO??? headers_to_send = ''

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response)
    client.close()
    
    print ("Served one request/connection!")
    print ()

# We will never actually get here.
# Close the listening socket
sock.close()
