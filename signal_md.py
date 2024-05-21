import time
import json

import sys
sys.path.insert(1, '../message_md/')
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
JSON_ATTACHMENT_CUSTOM_FILENAME = "custom_filename"

# -----------------------------------------------------------------------------
#
# Grab the attachments meta data from the message.
# Parameters:
# 
#   - json - attachments metadata in JSON from the Signal output
#   - the_message - the message the attachment(s) came in 
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
#        'custom_filename': 'IMG_8409.jpg',
#        'width': 1200, 
#        'height': 1600, 
#        'voiceNote': False, 
#        'key': '2OPGWwWCxSox7LKgNP9McvHISOaoTU+qveUqKGKYvZvWo78RKlsW6MFG1JTXPUZWg37+KQo1husCa7LKVIkDWw==', 
#        'digest': 'CXNyaQWkBpB2T7yEAJChZcwm6Jd95l677YFiJe56KcU=', 
#        'blurhash': 'LfLf]d-j%1-p~VoyNIogM_WERkWB'
#    }
# -----------------------------------------------------------------------------
def extract_attachment_data(json_attachments, the_message):
    
    num_attachments = 0
    
    for data in json_attachments:
        the_attachment = attachment.Attachment()
        try:
            the_attachment.type = data[JSON_ATTACHMENT_CONTENT_TYPE]
            the_attachment.id = data[JSON_ATTACHMENT_ID]
            the_attachment.size = data[JSON_ATTACHMENT_SIZE]
            the_attachment.filename = data[JSON_ATTACHMENT_FILENAME]

            try:
                the_attachment.custom_filename = data[JSON_ATTACHMENT_CUSTOM_FILENAME]
            except:
                pass

            the_attachment.width = data[JSON_ATTACHMENT_WIDTH]
            the_attachment.height = data[JSON_ATTACHMENT_HEIGHT]
            the_attachment.voice_note = data[JSON_ATTACHMENT_VOICE_NOTE]
            the_message.add_attachment(the_attachment)
            num_attachments += 1
        except:
            pass

    return num_attachments

# -----------------------------------------------------------------------------
#
# Read the message from JSON into a Message or a Reaction object.
#
# Parameters:
#
#   - type - type of message, either JSON_SYNC_MESSAGE or JSON_DATA_MESSAGE
#   - line - the entire message contents
#   - the_message - the target Message object where the values will go
#   - the_reaction - the emoji used, if any
#   - the_config - all of the config including Group and Person objects
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
def extract_message(type, line, the_message, the_reaction, the_config):

    time_in_seconds = 0
    to_person = person.Person()
    author = person.Person() # if a JSON_QUOTE in reply to the author

    data = line[JSON_DATA]
    
    try:
        the_message.phone_number = data[JSON_SOURCE][JSON_NUMBER]
    except:
        # this seems important, because no number and no clue who sent it,
        # then there should be some error communicatd to the user
        pass 
    
    try:
        the_message.time_stamp = data[JSON_TIMESTAMP]
        time_in_seconds = int(int(data[JSON_TIMESTAMP])/1000)
        # convert the time seconds since epoch to a time.struct_time object
        the_message.time = time.localtime(time_in_seconds)

    except Exception as e:
        print(e) 
        pass

    if type == JSON_DATA_MESSAGE:
        json_message = data[JSON_DATA_MESSAGE]

    elif type == JSON_SYNC_MESSAGE:
        json_sent = data[JSON_SYNC_MESSAGE][JSON_SENT]
        json_message = json_sent[JSON_MESSAGE]

        # the destination is not always present
        try:
            dest_phone_number = json_sent[JSON_DESTINATION][JSON_NUMBER]
            to_person = the_config.get_person_by_number(dest_phone_number)
            the_message.to_slugs.append(to_person.slug)
        except:
            pass

    try:
        the_message.body = json_message[JSON_BODY]
    except:
        try:
            source = the_config.get_person_by_number(the_message.phone_number)
            the_reaction.from_slug = source.slug
            json_reaction = json_message[JSON_REACTION]
            the_reaction.emoji = json_reaction[JSON_EMOJI]
            the_reaction.target_time_sent = json_reaction[JSON_TARGET_SENT_TIMESTAMP]
        except Exception as e:
            pass

    # see if it's a reply
    try:
        the_quote = json_message[JSON_QUOTE]
        the_message.quote.id = the_quote[JSON_QUOTE_ID]
        the_message.quote.text = the_quote[JSON_QUOTE_TEXT]
#       @todo need to refactor this to use phone#
        the_message.quote.author_name = author.first_name
        the_message.quote.author_slug = author.slug
    except:
        pass

    # see if it's a group message
    try:
        group = json_message[JSON_GROUPV2]
        group_id = group[JSON_GROUP_ID]
        the_message.group_slug = the_config.get_group_slug(group_id)
    except:
        pass

    # see if it's an attachment
    try:
        json_attachments = json_message[JSON_ATTACHMENTS]
        extract_attachment_data(json_attachments, the_message)
    except:
        pass

    if len(the_message.phone_number):
        the_person = the_config.get_person_by_number(the_message.phone_number)
        the_message.fromSlug = the_person.slug

    if the_message.time:
        try:
            the_message.dateStr = time.strftime("%Y-%m-%d", the_message.time)
            the_message.timeStr = time.strftime("%H:%M", the_message.time)
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
def processLine(line, the_message, the_reaction, the_config):

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
            extract_message(JSON_SYNC_MESSAGE, line, the_message, the_reaction, the_config)
        else:
            extract_message(JSON_DATA_MESSAGE, line, the_message, the_reaction, the_config)

        if not len(the_message.to_slugs):
            the_message.to_slugs.append(the_config.me.slug)

        result = True

    return result

# parse a line from the signald output file
def parse_line(the_line, the_message, the_reaction, the_config):

    result = False
    
    json_message = json.loads(the_line)

    if JSON_TYPE in json_message:
        if json_message[JSON_TYPE] == JSON_INCOMING_MESSAGE:
            result = processLine(json_message, the_message, the_reaction, theConfig)

    return result

# go though each line of the source file and process it by loading each message
# into a `Message` object and adding it to the `Messages` collection
def loadMessages(filename, messages, reactions, the_config):

    ignored = 0
    parsed = 0
    errored = 0
    no_body_or_attachment = 0
    i = 0

    try:
        source_file = open(filename, 'r', encoding="utf-8")
    except Exception as e:
        print(the_config.getStr(the_config.STR_COULD_NOT_OPEN_MESSAGES_FILE) + ": " + filename)
        print(e)
        return i

    while True:
        line = ""

        try:
            line = source_file.readline()
            if not line:
                break

            line = line.encode("utf-8")
            line = line.rstrip()

            try:
                the_message = message.Message()
                the_reaction = message.Reaction()
                if parse_line(line, the_message, the_reaction, theConfig):
                    parsed += 1

                    if the_reaction.emoji:
                        reactions.append(the_reaction) 

                    if len(the_message.body) or len(the_message.attachments):
                        messages.append(the_message)
                    else:
                        no_body_or_attachment +=1

            except Exception as exception1:
                errored += 1

        except Exception as exception2: 
            ignored += 1 # failed

        i += 1

    if the_config.debug:
        print("parsed: " + str(parsed))
        print("errored: " + str(errored))
        print("no body or attachment: " + str(no_body_or_attachment))
        print("ignored: " + str(ignored))

    source_file.close()

    return i

# main

the_messages = []
the_reactions = []
the_config = config.Config()

if message_md.setup(the_config, markdown.YAML_SERVICE_SIGNAL):

    # needs to be after setup so the command line parameters override the
    # values defined in the settings file
    message_md.getMarkdown(the_config, load_messages, the_messages, the_reactions)