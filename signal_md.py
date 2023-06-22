import time
import json
import os
import shutil
from datetime import date
from datetime import datetime
from pathlib import Path
from os.path import exists

import sys
sys.path.insert(1, '../message_md/')
import message_md

# files
MESSAGE_FILE_NAME = "messages.json"
MESSAGES_COPY_FILE_NAME = "messages_copy"
MESSAGES_SUFFIX = "json"

# string fields
LANGUAGE_FIELD = "language"
STRING_NUMBER = "number"
STRING_TEXT = "text"

# signald message types
JSON_INCOMING_MESSAGE = "IncomingMessage"

# fields in signald JSON file (MESSAGE_FILE_NAME)
JSON_TYPE = "type"
JSON_DATA = "data"
JSON_BODY = "body"
JSON_SOURCE = "source"
JSON_NUMBER = "number"
JSON_ACCOUNT = "account"
JSON_TIMESTAMP = "timestamp"
JSON_DATA_MESSAGE = "data_message"
JSON_REACTION = "reaction"
JSON_EMOJI = "emoji"
JSON_SYNC_MESSAGE = "sync_message"
JSON_SENT = "sent"
JSON_MESSAGE = "message"
JSON_GROUPV2 = "groupV2"
JSON_GROUP_ID = "id"
JSON_DESTINATION = "destination"
JSON_UUID = "uuid"
JSON_TARGET_SENT_TIMESTAMP = "targetSentTimestamp"
JSON_TARGET_AUTHOR = "targetAuthor"

JSON_QUOTE = "quote"
JSON_QUOTE_ID = "id"
JSON_QUOTE_TEXT = "text"
JSON_QUOTE_AUTHOR = "author"

JSON_ATTACHMENTS = "attachments"
JSON_ATTACHMENT_CONTENT_TYPE = "contentType"
JSON_ATTACHMENT_ID = "id"
JSON_ATTACHMENT_SIZE = "size"
JSON_ATTACHMENT_FILENAME = "storedFilename"
JSON_ATTACHMENT_WIDTH = "width"
JSON_ATTACHMENT_HEIGHT = "height"
JSON_ATTACHMENT_VOICE_NOTE = "voiceNote"
JSON_ATTACHMENT_CUSTOM_FILENAME = "customFilename"

# -----------------------------------------------------------------------------
#
# Grab the attachments meta data from the message.
# Parameters:
# 
#   - json - attachments metadata in JSON from the Signal output
#   - message - the message the attachment(s) came in 
#
# Notes
#   - the attachment metadata comes in a separate message in the JSON output
#   - the actual attachment files themselves have a unique ID assigned to them
#     with no file suffix and are stored in a subfolder `attachments`
#
# Returns the number of attachments
#
# Notes:
#   - example JSON format of an attachment
#     {
#        'contentType': 'image/jpeg', 
#        'id': 'ChyDimZpbMTPEnAhhUL7', 
#        'size': 354057, 
#        'storedFilename': '/signald/attachments/ChyDimZpbMTPEnAhhUL7', 
#        'customFilename': 'IMG_8409.jpg',
#        'width': 1200, 
#        'height': 1600, 
#        'voiceNote': False, 
#        'key': '2OPGWwWCxSox7LKgNP9McvHISOaoTU+qveUqKGKYvZvWo78RKlsW6MFG1JTXPUZWg37+KQo1husCa7LKVIkDWw==', 
#        'digest': 'CXNyaQWkBpB2T7yEAJChZcwm6Jd95l677YFiJe56KcU=', 
#        'blurhash': 'LfLf]d-j%1-p~VoyNIogM_WERkWB'
#    }
# -----------------------------------------------------------------------------
def extractAttachmentData(jsonAttachments, message):
    numAttachments = 0
    
    for data in jsonAttachments:
        attachment = message_md.Attachment()
        try:
            attachment.type = data[JSON_ATTACHMENT_CONTENT_TYPE]
            attachment.id = data[JSON_ATTACHMENT_ID]
            attachment.size = data[JSON_ATTACHMENT_SIZE]
            attachment.fileName = data[JSON_ATTACHMENT_FILENAME]

            try:
                attachment.customFileName = data[JSON_ATTACHMENT_CUSTOM_FILENAME]
            except:
                pass

            attachment.width = data[JSON_ATTACHMENT_WIDTH]
            attachment.height = data[JSON_ATTACHMENT_HEIGHT]
            attachment.voiceNote = data[JSON_ATTACHMENT_VOICE_NOTE]
            message.addAttachment(attachment)

            numAttachments += 1
        except:
            pass

    return numAttachments

# -----------------------------------------------------------------------------
#
# Read the message from JSON into a Message or a Reaction object.
#
# Parameters:
#
#   - type - type of message, either JSON_SYNC_MESSAGE or JSON_DATA_MESSAGE
#   - line - the entire message contents
#   - message - the target Message object where the values will go
#   - reaction - the emoji used, if any
#   - config - all of the config including Group and Person objects
#
# Notes:
#
# This part shows the receiver (`account`) and the sender (`source:number`)
#
#    "data":{ 
#        "account":"+12895551212",
#        "source":{
#            "number":"+14165551313",
#
# and for a `data-message` this part the body of the message excluding
# inconsequential fields 
#
#      "data_message":{
#         "timestamp":1668444176427,
#         "body":"Is the heat on? I am literally freezing",
# 
# OR if a `sync-message` - a copy of the message sent to oneself...
#
# replying with "I agree" (`body`) to "You are amazing!" (`quote > text`)
#
#      "sync_message":{
#         "sent":{
#             "destination":{"uuid":"db8ca91a-af41-4365-b498-b864117ce4bb"},
#             "timestamp":1668613286231,
#             "message":{
#                 "timestamp":1668613286231,
#                 "body":"I agree",
#                 "quote":{
#                     "id":1668613239290,
#                     "author":{"uuid":"db8ca91a-af41-4365-b498-b864117ce4bb"},
#                     "text":"You are amazing!",
#                     "mentions":[]
# -----------------------------------------------------------------------------
def extractMessage(type, line, message, reaction, config):

    timeInSeconds = 0
    toPerson = message_md.Person()  
    author = message_md.Person() # if a JSON_QUOTE in reply to the author

    data = line[JSON_DATA]
    
    try:
        message.phoneNumber = data[JSON_SOURCE][JSON_NUMBER]
    except:
        # this seems important, because no number and no clue who sent it,
        # then there should be some error communicatd to the user
        pass 
    
    try:
        message.timeStamp = data[JSON_TIMESTAMP]
        timeInSeconds = int(int(data[JSON_TIMESTAMP])/1000)
        # convert the time seconds since epoch to a time.struct_time object
        message.time = time.localtime(timeInSeconds)

    except Exception as exception: 
        pass

    if type == JSON_DATA_MESSAGE:
        jsonMessage = data[JSON_DATA_MESSAGE]

    elif type == JSON_SYNC_MESSAGE:
        jsonSent = data[JSON_SYNC_MESSAGE][JSON_SENT]
        jsonMessage = jsonSent[JSON_MESSAGE]

        # the destination is not always present
        try:
            destPhoneNumber = jsonSent[JSON_DESTINATION][JSON_NUMBER]
            toPerson = config.getPersonByNumber(destPhoneNumber)
            message.destinationSlug = toPerson.slug
        except:
            pass

    try:
        message.body = jsonMessage[JSON_BODY]
    except:
        try:
            source = config.getPersonByNumber(message.phoneNumber)
            reaction.sourceSlug = source.slug
            jsonReaction = jsonMessage[JSON_REACTION]
            reaction.emoji = jsonReaction[JSON_EMOJI]
            reaction.targetTimeSent = jsonReaction[JSON_TARGET_SENT_TIMESTAMP]
            reactions.append(reaction)
        except Exception as e:
            pass

    # see if it's a reply
    try:
        theQuote = jsonMessage[JSON_QUOTE]
        message.quote.id = theQuote[JSON_QUOTE_ID]
        message.quote.text = theQuote[JSON_QUOTE_TEXT]
#       @todo need to refactor this to use phone#
        message.quote.authorName = author.firstName
        message.quote.authorSlug = author.slug
    except:
        pass

    # see if it's a group message
    try:
        group = jsonMessage[JSON_GROUPV2]
        groupId = group[JSON_GROUP_ID]
        message.groupSlug = config.getGroupSlug(groupId)
    except:
        pass

    # see if it's an attachment
    try:
        jsonAttachments = jsonMessage[JSON_ATTACHMENTS]
        extractAttachmentData(jsonAttachments, message)
    except:
        pass

    if len(message.phoneNumber):
        person = config.getPersonByNumber(message.phoneNumber)
        message.sourceSlug = person.slug

    if message.time:
        try:
            message.dateStr = time.strftime("%Y-%m-%d", message.time)
            message.timeStr = time.strftime("%H:%M", message.time)
        except Exception as e:
            print(e)

    return

# -----------------------------------------------------------------------------
#
# Determine if a JSON line is a `data` (`account` and `source` are different)
# or a `sync` message (`account` and `source` are the same)
#
# The receiver is `data:account` and the sender `data:source:number`
#
#    "data":{ 
#        "account":"+12895551212",
#        "source":{
#            "number":"+14165551313",
#
# -----------------------------------------------------------------------------
def processLine(line, message, reaction, config):

    number = 0
    account = 0
    noAccount = 0
    noNumber = 0
    result = False

    data = line[JSON_DATA]

    try:
        account = data[JSON_ACCOUNT]
    except: 
        noAccount += 1

    try:
        number = data[JSON_SOURCE][JSON_NUMBER]
    except: 
        noNumber += 1

    if len(account) and len(number):
        if account == number:
            extractMessage(JSON_SYNC_MESSAGE, line, message, reaction, config)
        else:
            extractMessage(JSON_DATA_MESSAGE, line, message, reaction, config)

        if len(message.destinationSlug)==0:
            message.destinationSlug = config.mySlug

        result = True

    return result

# parse a line from the signald JSON output file
def parseLine(theLine, message, reaction, config):

    result = False
    
    jsonMessage = json.loads(theLine)

    if JSON_TYPE in jsonMessage:
        if jsonMessage[JSON_TYPE] == JSON_INCOMING_MESSAGE:
            result = processLine(jsonMessage, message, reaction, config)

    return result

# go though each line of the source file and process it by loading each message
# into a `Message` object and adding it to the `Messages` collection
def loadMessages(fileName, messages, reactions, config):

    ignored = 0
    parsed = 0
    errored = 0
    noBodyOrAttachment = 0
    i = 0

    try:
        sourceFile = open(fileName, 'r', encoding="utf-8")
    except Exception as e:
        print(config.getStr(config.STR_COULD_NOT_OPEN_MESSAGES_FILE) + ": " + fileName)
        print(e)
        return i

    while True:
        line = ""

        try:
            line = sourceFile.readline()
            if not line:
                break

            line = line.encode("utf-8")
            line = line.rstrip()

            try:
                message = message_md.Message()
                reaction = message_md.Reaction()
                if parseLine(line, message, reaction, config):
                    parsed += 1

                    if len(message.body) or len(message.attachments):
                        messages.append(message)
                    else:
                        noBodyOrAttachment +=1

            except Exception as exception1:
                errored += 1

        except Exception as exception2: 
            ignored += 1 # failed

        i += 1

    if config.debug:
        print("parsed: " + str(parsed))
        print("errored: " + str(errored))
        print("no body or attachment: " + str(noBodyOrAttachment))
        print("ignored: " + str(ignored))

    sourceFile.close()

    return i

# main

messages = []
reactions = []

config = message_md.Config()

if message_md.setup(config, message_md.YAML_SERVICE_SIGNAL):

    # needs to be after setup so the command line parameters override the
    # values defined in the settings file
    message_md.markdown(config, loadMessages, messages, reactions)