import os
import re
import base64
import keyring
from cryptography.fernet import Fernet

# Make sure the key, Fernet objects within scope of future dependencies
# by setting to here (to nothing, for now)
frn = Fernet(base64.b64encode(bytes(list(range(32)))))
key = bytes(0)

if os.path.isfile('./key'):  # Check the 'key' file already exists

    # attempts to open a 'key' file where we store the Fernet key
    # (`rb` means `Read Binary` from file)
    keyf = open("key", 'rb')
    key = keyf.read()
    keyf.close()  # close the key file

else:
    # This is for when the 'key' file doesn't exist or was deleted

    print("Key did not exist. Creating...")

    # attempts to create/open a 'key' file where we store the
    # Fernet key (wb+ means Write Binary to file with additional
    # read privileges)
    keyf = open("key", 'wb+')

    # generates a Fernet key and saves that key to the 'key' file
    key = Fernet.generate_key()
    keyf.write(key)

    keyf.close()  # close the key file

# create Fernet object to do encryption using our key from above
frn = Fernet(key)

print("[1] Store bot token in key ring", "[2] Store bot token to disk")
question = "Should we keep token in keyring or store to disk? [1-2]>\n"
howToStoreToken = int(input(question))
correctToken = False

while not(howToStoreToken == 1 or howToStoreToken == 2):
    howToStoreToken = int(input(question))  # Keep asking for a 1 or 2

# basic regex pattern checks on presumed token
correctToken = False
while not(correctToken):
    token = input("What's the bot token? > ")
    clientSecretPat = re.compile("^.{32}$")
    clientIDPat = re.compile("^\d{18}$")
    tokenPat = re.compile("^.{59}$")
    wrong = "The string you've entered looks like the %s.\
        Are you sure you copied the correct field?"
    if tokenPat.match(token):
        print("Token pattern matches! 👍🏽")
        correctToken = True
        continue
    elif clientSecretPat.match(token):
        print(wrong % "client secret")
        continue
    elif clientIDPat.match(token):
        print(wrong % "client ID")
        continue
if howToStoreToken == 1:
    # ask the user for the Discord token, then writes the token as password
    # into the keyring with the Fernet key as the username
    keyring.set_password("system", key, (
        input("What is the secret?> ")))
    if not keyring.get_password("system", key.decode('utf-8')) is None:
        print("Your token has been stored in the file system keyring!")
    else:
        print("Could not store token in the file system keyring!")
elif howToStoreToken == 2:
    tokenFilename = input("What should be the token filename?> ")
    while(os.path.isfile('./' + tokenFilename)):
        print(tokenFilename, "already exists.\nChoose another name.")
        tokenFilename = input("What should be the token filename?> ")
    try:
        # try-finally block for error `IOError` on opening token file for
        # writing binary

        # attempt to create/open a 'tokenFilename' file where we store the
        # encrypted Discord token (we don't need to read 'tokenFilename'
        # here, so we only need write privileges)
        tokenf = open(tokenFilename, 'wb')

        # ask the user for the Discord token, then encodes as binary, then
        # encrypts the binary, and then writes binary to 'token' file
        tokenf.write(frn.encrypt(str.encode(token)))

    except PermissionError as error:
        print(error, "\nCould not write token file. Check permissions.")
    finally:
        tokenf.close()  # close the file `token`
        if(os.path.isfile('./' + tokenFilename)):
            print("Your token has been stored in a file!")

# read and write `.gitignore` to make sure we don't accidentally upload
# key or token
try:
    # open `.gitignore` as a read only
    gitignoref = open(".gitignore", 'r')

    # store the content of `.gitignore`
    gitignore = gitignoref.read()

    # open `.gitignore` append mode (write starting at the end of the file)
    gitignoref = open(".gitignore", 'a')

    # regular expression pattern matching the word 'key' anywhere
    keyRE = re.compile("key", re.MULTILINE)

    # if the word 'key' is not found in the content of `.gitignore`
    if(re.search(keyRE, gitignore) is None):

        # then add 'key' to the next line in `.gitignore`
        gitignoref.write("\nkey")

    # if the word 'token' is not found in the content of `.gitignore`
    if(howToStoreToken == "2"):

        # regular expression pattern matching the word 'token' anywhere
        tokenRE = re.compile(tokenFilename, re.MULTILINE)

        if(re.search(tokenRE, gitignore) is None):
            # then add 'key' to the next line in `.gitignore`
            gitignoref.write("\n" + tokenFilename)
except PermissionError as error:
    print(error, "\nCould not write gitignore file. Check permissions.")
finally:
    # Below code will run in any event (whether there is an error or not)
    gitignoref.close()  # close the file `.gitignore`

# Change the mod-logs channel in `discordbot.py`
question = "What is your `mod-logs` channel ID?"
modlogsID = input(question)
channelIDRe = '\d{18}'
channelIDPat = re.compile("^" + channelIDRe + "$")
while not(channelIDPat.match(modlogsID)):
    print("Input ID incorrect. See https://bit.ly/31q1Qlh for instructions.")
    modlogsID = input(question)
if os.path.isfile("discordbot.py"):
    discordbotf = open("discordbot.py", 'r')
    discordbot = discordbotf.readlines()
    discordbotf.close()

    modlogsReComp = re.compile("(\s+modlogs = )(" + channelIDRe + ")(.*)")

    for lineNum in range(len(discordbot)):
        print(lineNum)
        if re.search(modlogsReComp, discordbot[lineNum]):
            discordbot[lineNum] = re.sub(
                modlogsReComp, r"\1 012345678901234567 \3", discordbot[lineNum]
            )
            break

    discordbotf = open("discordbot.py", 'w')
    discordbotf.writelines(discordbot)
    discordbotf.close()
