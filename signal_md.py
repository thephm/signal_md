import time
import json

import sys
sys.path.insert(1, '../message_md/')
import message_md
import message_md
import config
import markdown
import attachment
import message
import person

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
#   - theMessage - the message the attachment(s) came in 
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
def extractAttachmentData(jsonAttachments, theMessage):
    numAttachments = 0
    
    for data in jsonAttachments:
        theAttachment = attachment.Attachment()
        try:
            theAttachment.type = data[JSON_ATTACHMENT_CONTENT_TYPE]
            theAttachment.id = data[JSON_ATTACHMENT_ID]
            theAttachment.size = data[JSON_ATTACHMENT_SIZE]
            theAttachment.fileName = data[JSON_ATTACHMENT_FILENAME]

            try:
                theAttachment.customFileName = data[JSON_ATTACHMENT_CUSTOM_FILENAME]
            except:
                pass

            theAttachment.width = data[JSON_ATTACHMENT_WIDTH]
            theAttachment.height = data[JSON_ATTACHMENT_HEIGHT]
            theAttachment.voiceNote = data[JSON_ATTACHMENT_VOICE_NOTE]
            theMessage.addAttachment(theAttachment)
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
#   - theMessage - the target Message object where the values will go
#   - theReaction - the emoji used, if any
#   - theConfig - all of the config including Group and Person objects
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
def extractMessage(type, line, theMessage, theReaction, theConfig):

    timeInSeconds = 0
    toPerson = person.Person()  
    author = person.Person() # if a JSON_QUOTE in reply to the author

    data = line[JSON_DATA]
    
    try:
        theMessage.phoneNumber = data[JSON_SOURCE][JSON_NUMBER]
    except:
        # this seems important, because no number and no clue who sent it,
        # then there should be some error communicatd to the user
        pass 
    
    try:
        theMessage.timeStamp = data[JSON_TIMESTAMP]
        timeInSeconds = int(int(data[JSON_TIMESTAMP])/1000)
        # convert the time seconds since epoch to a time.struct_time object
        theMessage.time = time.localtime(timeInSeconds)

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
            toPerson = theConfig.getPersonByNumber(destPhoneNumber)
            theMessage.destinationSlug = toPerson.slug
        except:
            pass

    try:
        theMessage.body = jsonMessage[JSON_BODY]
    except:
        try:
            source = theConfig.getPersonByNumber(theMessage.phoneNumber)
            theReaction.sourceSlug = source.slug
            jsonReaction = jsonMessage[JSON_REACTION]
            theReaction.emoji = jsonReaction[JSON_EMOJI]
            theReaction.targetTimeSent = jsonReaction[JSON_TARGET_SENT_TIMESTAMP]
        except Exception as e:
            pass

    # see if it's a reply
    try:
        theQuote = jsonMessage[JSON_QUOTE]
        theMessage.quote.id = theQuote[JSON_QUOTE_ID]
        theMessage.quote.text = theQuote[JSON_QUOTE_TEXT]
#       @todo need to refactor this to use phone#
        theMessage.quote.authorName = author.firstName
        theMessage.quote.authorSlug = author.slug
    except:
        pass

    # see if it's a group message
    try:
        group = jsonMessage[JSON_GROUPV2]
        groupId = group[JSON_GROUP_ID]
        theMessage.groupSlug = theConfig.getGroupSlug(groupId)
    except:
        pass

    # see if it's an attachment
    try:
        jsonAttachments = jsonMessage[JSON_ATTACHMENTS]
        extractAttachmentData(jsonAttachments, theMessage)
    except:
        pass

    if len(theMessage.phoneNumber):
        thePerson = theConfig.getPersonByNumber(theMessage.phoneNumber)
        theMessage.sourceSlug = thePerson.slug

    if theMessage.time:
        try:
            theMessage.dateStr = time.strftime("%Y-%m-%d", theMessage.time)
            theMessage.timeStr = time.strftime("%H:%M", theMessage.time)
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
def processLine(line, theMessage, theReaction, theConfig):

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
            extractMessage(JSON_SYNC_MESSAGE, line, theMessage, theReaction, theConfig)
        else:
            extractMessage(JSON_DATA_MESSAGE, line, theMessage, theReaction, theConfig)

        if len(theMessage.destinationSlug)==0:
            theMessage.destinationSlug = theConfig.mySlug

        result = True

    return result

# parse a line from the signald JSON output file
def parseLine(theLine, theMessage, theReaction, theConfig):

    result = False
    
    jsonMessage = json.loads(theLine)

    if JSON_TYPE in jsonMessage:
        if jsonMessage[JSON_TYPE] == JSON_INCOMING_MESSAGE:
            result = processLine(jsonMessage, theMessage, theReaction, theConfig)

    return result

# go though each line of the source file and process it by loading each message
# into a `Message` object and adding it to the `Messages` collection
def loadMessages(fileName, messages, reactions, theConfig):

    ignored = 0
    parsed = 0
    errored = 0
    noBodyOrAttachment = 0
    i = 0

    try:
        sourceFile = open(fileName, 'r', encoding="utf-8")
    except Exception as e:
        print(theConfig.getStr(theConfig.STR_COULD_NOT_OPEN_MESSAGES_FILE) + ": " + fileName)
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
                theMessage = message.Message()
                theReaction = message.Reaction()
                if parseLine(line, theMessage, theReaction, theConfig):
                    parsed += 1

                    if theReaction.emoji:
                        reactions.append(theReaction) 

                    if len(theMessage.body) or len(theMessage.attachments):
                        messages.append(theMessage)
                    else:
                        noBodyOrAttachment +=1

            except Exception as exception1:
                errored += 1

        except Exception as exception2: 
            ignored += 1 # failed

        i += 1

    if theConfig.debug:
        print("parsed: " + str(parsed))
        print("errored: " + str(errored))
        print("no body or attachment: " + str(noBodyOrAttachment))
        print("ignored: " + str(ignored))

    sourceFile.close()

    return i

# main

theMessages = []
theReactions = []
theConfig = config.Config()

if message_md.setup(theConfig, markdown.YAML_SERVICE_SIGNAL):

    # needs to be after setup so the command line parameters override the
    # values defined in the settings file
    message_md.getMarkdown(theConfig, loadMessages, theMessages, theReactions)