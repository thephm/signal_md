import time
import json
import os
import shutil
from datetime import date
from datetime import datetime
from pathlib import Path
from os.path import exists

# some constants
SPACE = " "
TWO_SPACES = SPACE + SPACE
MD_QUOTE = ">" + SPACE
NEW_LINE = "\n"

# YAML front matter 
YAML_DASHES = "---" + NEW_LINE
YAML_PERSON_SLUGS = "person-slugs"
YAML_SERVICE_SLUG = "service-slug"
YAML_TAGS = "tags"
YAML_DATE = "date"
YAML_TIME = "time"
YAML_SERVICE_SIGNAL = "signal"
TAG_CHAT = "chat"

# files
CONFIG_FOLDER = "config"
SETTINGS_FILE_NAME= os.path.join(CONFIG_FOLDER, "settings.json")
STRINGS_FILE_NAME = os.path.join(CONFIG_FOLDER, "strings.json")
PEOPLE_FILE_NAME  = os.path.join(CONFIG_FOLDER, "people.json")
GROUPS_FILE_NAME  = os.path.join(CONFIG_FOLDER, "groups.json")
MIME_TYPES_FILE_NAME = os.path.join(CONFIG_FOLDER, "MIMETypes.json")
MESSAGE_FILE_NAME = "messages.json"
MESSAGES_COPY_FILE_NAME = "messages_copy"
MESSAGES_SUFFIX = "json"

# string fields
LANGUAGE_FIELD = "language"
STRING_NUMBER = "number"
STRING_TEXT = "text"

# languages
ENGLISH = 1

# string numbers
STR_NOT_FOUND = 0
STR_AT = 1
STR_ERROR = 2
STR_COULD_NOT_OPEN_FILE = 3
STR_PERSON_NOT_FOUND = 4
STR_FAILED_TO_READ_LINE = 5
STR_FAILED_TO_WRITE = 6
STR_COULD_NOT_LOAD_MIME_TYPES = 7
STR_UNKNOWN_MIME_TYPE = 8
STR_COULD_NOT_MOVE_THE_ATTACHMENT = 9
STR_COULD_NOT_MOVE_MESSAGES_FILE = 10
STR_COULD_NOT_OPEN_MESSAGES_FILE = 11
STR_COULD_CREATE_ARCHIVE_FOLDER = 12

# within array of string fields (after loaded)
STRINGS_LANGUAGE_INDEX = 0
STRINGS_NUMBER_INDEX = 1
STRINGS_TEXT_INDEX = 2

OUTPUT_FILE_EXTENSION = ".md"

## configuration field names (SETTINGS_FILE_NAME)
SETTING_LANGUAGE = "language"
SETTING_MY_SLUG = "my-slug"
SETTING_SOURCE_FOLDER = "source-folder"
SETTING_MESSAGES_FILE = "messages-file"
SETTING_ATTACHMENTS_SUB_FOLDER = "attachments-sub-folder"
SETTING_INCLUDE_TIMESTAMP = "include-timestamp"
SETTING_INCLUDE_QUOTE = "include-quote"
SETTING_COLON_AFTER_CONTEXT = "colon-after-context" 
SETTING_TIME_NAME_SEPARATE = "time-name-separate"
SETTING_MEDIA_SUBFOLDER = "media-subfolder"
SETTING_IMAGE_EMBED = "image-embed"
SETTING_IMAGE_WIDTH = "image-width"
SETTING_ARCHIVE_FOLDER = "archive-folder"
SETTING_OUTPUT_FOLDER = "output-folder"
SETTING_GROUPS_FOLDER = "groups-folder"
SETTING_INCLUDE_REACTIONS = "include-reactions"
SETTING_FOLDER_PER_PERSON = "folder-per-person"
SETTING_FILE_PER_PERSON = "file-per-person"
SETTING_FILE_PER_DAY = "file-per-day"
SETTING_DAILY_NOTES_FOLDER = "daily-notes-folder"

MAX_LEN_QUOTED_TEXT = 70

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

# fields in people file (PEOPLE_FILE_NAME)
PERSON_FIELD_NUMBER = "number"
PERSON_FIELD_SLUG = "person-slug"
PERSON_FIELD_FIRST_NAME = "first-name"

# fields in groups file (GROUPS_FILE_NAME)
GROUP_COLLECTION = "groups"
GROUP_FIELD_ID = "id"
GROUP_FIELD_SLUG = "slug"
GROUP_FIELD_DESCRIPTION = "description"
GROUP_FIELD_PEOPLE = "people"

# within array of person fields (after loaded)
# #todo this is STUPID and needs to be removed!
PERSON_INDEX_NUMBER = 0
PERSON_INDEX_SLUG = 1
PERSON_INDEX_FIRST_NAME = 2

# global collections
people = []
person = []
groups = []
settings = []
Strings = []

# set the default values for the settings
Language = ENGLISH # English
MySlug = ""
SourceFolder = "."
MessagesFile = os.path.join(SourceFolder, "messages.json")
AttachmentsFolder = os.path.join(SourceFolder, "attachments")
MediaSubFolder = "media"
ImageEmbed = True
ImageWidth = 450
ArchiveFolder = "archive"
OutputFolder = "output"
GroupsFolder = os.path.join(OutputFolder, "groups")
DailyNotesFolder = ""
IncludeTimestamp = True
IncludeQuote = True
ColonAfterContext = False
IncludeReactions = False
TimeNameSeparate = False
FolderPerPerson = True
FilePerPerson = True
FilePerDay = True

MIMETypes = []

# not used yet, thinking about it
class Setting:
    def __init__(self):
        self.key = ""
        self.value = 0

class String:
    def __init__(self):
        self.number = 0
        self.language = 0
        self.text = ""

class Attachment:
    def __init__(self):
        self.type = ""    # contentType
        self.id = ""
        self.size = 0
        self.fileName = ""
        self.customFileName = ""
        self.width = 0
        self.height = 0
        self.voiceNote = False

    def isImage(self):
        isImage = False

        if (self.type[:5] == "image"):
            isImage = True

        return isImage

    # Get the file name with suffix based on it's content type
    def withSuffix(self):

        global MIMETypes
        
        fileName = self.id

        try:
            suffix = MIMETypes[self.type]
            if (len(suffix)):
                fileName += "." + suffix 
        except:
            print(getStr(STR_UNKNOWN_MIME_TYPE) + ": '" + self.type + "' (" + self.id + ')')

        return fileName

    # Generates the Markdown for media links e.g. [[photo.jpg]]
    def generateLink(self):
            
        global ImageEmbed
        global ImageWidth
        global MediaSubFolder

        link = ""

        # originally I would include 'media/file.jpg' but since Obsidian
        # finds any file in the vault, no need to tell it where it is
        fileName = self.withSuffix()
        if (len(fileName)):
            if (self.isImage() and ImageEmbed):
                link = "!"
            link += "[[" + fileName
            if (self.isImage() and ImageWidth):
                link += "|" + str(ImageWidth)
            link += "]]" + NEW_LINE

        return link

# The message being replied to, if this is a reply vs. a new message
class Quote:
    def __init__(self):
        self.id = ""         # timeStamp of the message being replied
        self.authorUUID = "" # UUID of person being quoted
        self.authorSlug = "" # person-slug being quoted
        self.authorName = "" # name of the person being quoted
        self.text = ""       # text being quoted

# Typically an emoji reaction to someone's message
class Reaction:
    def __init__(self):
        self.emoji = ""
        self.targetAuthorUUID = "" # peron being reacted to
        self.targetTimeSent = 0 # which timestamp the emoji relates to
        self.sourceSlug = "" # person who had the reaction

# An actual signal message
# 
# - If groupSlug is non-blank, then personSlug will be blank
# - If personSlug is non-blank, then groupSlug will be blank
class Message:
    def __init__(self):
        self.time = 0             # time.struct_time object
        self.timeStamp = 0        # original timestamp in the message
        self.dateStr = ""         # YYYY-MM-DD
        self.timeStr = ""         # hh:mm in 24 hour clock
        self.groupSlug = ""       # the group the message sent to
        self.phoneNumber = ""     # phone number of the sender
        self.sourceUUID = ""      # UUID of who the message is from
        self.sourceSlug = ""      # `person-slug` of who the message is from
        self.destinationUUID = "" # UUID of who the message was sent to
        self.destinationSlug = "" # `person-slug` who the message was sent to
        self.body = ""            # actual content of the message
        self.targetSentTimestamp = "" # which timestamp the emoji relates to
        self.processed = False    # True if the message been dealt with
        self.quote = Quote()      # quoted text if replying
        self.attachments = []
        self.reactions = []

    def __str__(self):
        output = str(self.timeStamp)
        output += "sourceSlug: " + self.sourceSlug + NEW_LINE
        output += "destinationSlug: " + self.destinationSlug + NEW_LINE
        output += "body: " + self.body
        return output

    # checks if this is a message sent to myself i.e. "Note to Self" feature
    def isNoteToSelf(self):
        result = False
        if (self.sourceSlug == self.destinationSlug):
            result = True
        return result

    def getDateStr(self):
        return time.strftime("%Y-%m-%d", self.dateStr)
        
    def getTimeStr(self):
        return time.strftime("%H:%M", self.timeStr)

    def hasAttachment(self):
        if len(self.attachments): return True
        else: return False

class DatedMessages:
    def __init__(self):
        self.dateStr = ""
        self.messages = []

class Person:
    def __init__(self):
        self.uuid = ""
        self.phoneNumber = ""
        self.slug = ""
        self.firstName = ""
        self.folderCreated = False
        self.messages = []  # collection of messages by day

class Group:
    def __init__(self):
        self.id = ""
        self.description = ""
        self.members = [] # collection of `Person.slug`s
        self.messages = [] # collection of messages by day

def loadMIMETypes():

    global MIMETypes

    result = True

    try:
        MIMETypesFile = open(MIME_TYPES_FILE_NAME, 'r')
        MIMETypes = json.load(MIMETypesFile)
    except:
        result = False
        print(getStr(STR_COULD_NOT_LOAD_MIME_TYPES))
    
    return result

def loadSettings():
    global Language
    global MySlug
    global SourceFolder
    global MessagesFile
    global AttachmentsFolder
    global IncludeTimestamp
    global IncludeQuote
    global ColonAfterContext
    global TimeNameSeparate
    global MediaSubFolder
    global ImageEmbed
    global ImageWidth
    global MediaSubFolder
    global ArchiveFolder
    global OutputFolder
    global GroupsFolder
    global IncludeReactions
    global FolderPerPerson
    global FilePerPerson
    global FilePerDay
    global DailyNotesFolder

    settingsFile = open(SETTINGS_FILE_NAME, 'r')
    settings = json.load(settingsFile)

    try:
        Language = int(settings[SETTING_LANGUAGE])
        MySlug = settings[SETTING_MY_SLUG]
        SourceFolder = settings[SETTING_SOURCE_FOLDER]
        MessagesFile = os.path.join(SourceFolder, settings[SETTING_MESSAGES_FILE])
        AttachmentsFolder = os.path.join(SourceFolder,settings[SETTING_ATTACHMENTS_SUB_FOLDER])
        ArchiveFolder = settings[SETTING_ARCHIVE_FOLDER]
        OutputFolder = settings[SETTING_OUTPUT_FOLDER]
        GroupsFolder = settings[SETTING_GROUPS_FOLDER]
        MediaSubFolder = settings[SETTING_MEDIA_SUBFOLDER]
        ImageEmbed = settings[SETTING_IMAGE_EMBED]
        ImageWidth = settings[SETTING_IMAGE_WIDTH]
        DailyNotesFolder = settings[SETTING_DAILY_NOTES_FOLDER]
        IncludeTimestamp = bool(settings[SETTING_INCLUDE_TIMESTAMP])
        IncludeQuote = bool(settings[SETTING_INCLUDE_QUOTE])
        ColonAfterContext = bool(settings[SETTING_COLON_AFTER_CONTEXT])
        TimeNameSeparate = bool(settings[SETTING_TIME_NAME_SEPARATE])
        IncludeReactions = bool(settings[SETTING_INCLUDE_REACTIONS])
        FolderPerPerson = bool(settings[SETTING_FOLDER_PER_PERSON])
        FilePerPerson = bool(settings[SETTING_FILE_PER_PERSON])
        FilePerDay = bool(settings[SETTING_FILE_PER_DAY])

    except:
        pass

    settingsFile.close()

# load strings
def loadStrings():
    stringsFile = open(STRINGS_FILE_NAME, 'r')

    for line in stringsFile:
        line = line.rstrip()
        x = json.loads(line)
        string = [x[LANGUAGE_FIELD], x[STRING_NUMBER], x[STRING_TEXT]]
        Strings.append(string)

    stringsFile.close()

# load the people
def loadPeople(people):

    peopleFile = open( PEOPLE_FILE_NAME, 'r', encoding="utf-8")

    for line in peopleFile:
        line = line.rstrip()
        x = json.loads(line)
        try:
            person = Person()
            person.phoneNumber = x[PERSON_FIELD_NUMBER]
            person.slug = x[PERSON_FIELD_SLUG]
            person.firstName = x[PERSON_FIELD_FIRST_NAME]
            people.append(person)
        except:
            pass

    peopleFile.close()

def loadGroups(groups):
    groupsFile = open(GROUPS_FILE_NAME, 'r', encoding="utf-8")
    jsonGroups = json.load(groupsFile)

    for jsonGroup in jsonGroups[GROUP_COLLECTION]:
        group = Group()
        try:
            group.id = jsonGroup[GROUP_FIELD_ID]
            group.slug = jsonGroup[GROUP_FIELD_SLUG]
            group.description = jsonGroup[GROUP_FIELD_DESCRIPTION]
            try:
                for personSlug in jsonGroup[GROUP_FIELD_PEOPLE]:
                    group.members.append(personSlug)
                groups.append(group)
            except:
                pass

        except:
            pass

    groupsFile.close()

# Lookup a person's first name from their phone number
def getFirstNameByNumber(number, people):
    
    global Strings

    firstName = ""
    person = getPersonByNumber(number, people)
    
    if (person):
        try: 
            firstName = person.firstName
        except:   
            print(getStr(STR_PERSON_NOT_FOUND))
            pass

    return firstName

# Lookup a person from their phone number
def getPersonByNumber(number, people):

    for person in people:
        if (person.phoneNumber == number):
            return person

# Lookup a person from their phone number
def getFirstNameBySlug(slug):

    firstName = ""

    for person in people:
        if (person.slug == slug):
            firstName = person.firstName
   
    return firstName

# Lookup a person from their UUID
def getPersonByUUID(uuid, people):
    for person in people:
        if (person.uuid == uuid):
            return person

# Lookup the group slug based on it's unique ID
def getGroupSlug(id, groups):
    slug = ""

    for group in groups:
        if (group.id == id):
            slug = group.slug
    
    return slug

# get a string out of strings based on its ID
def getStr(stringNumber):

    global Strings
    global Language

    result = ""

    for string in Strings:
        try:
            if (int(string[STRINGS_NUMBER_INDEX]) == int(stringNumber) and
                int(string[STRINGS_LANGUAGE_INDEX]) == Language):
                result = string[STRINGS_TEXT_INDEX]
        except:
            pass

    return result

# create a folder
def createFolder(folder):
    
    result = False

    try:
        Path(folder).mkdir(parents=True, exist_ok=True)
        result = True
    except Exception as e:
        print(e)

    return result

# -----------------------------------------------------------------------------
#
# Create folders for each persons' messages
# 
# -----------------------------------------------------------------------------
def createPersonFolders(people, folder, mySlug):

    global MediaSubFolder
    
    for person in people:
        try:
            personFolder = os.path.join(folder, person.slug)
            createFolder(personFolder)

            if (len(MediaSubFolder)):
                mediaFolder = os.path.join(personFolder, MediaSubFolder)
                createFolder(mediaFolder)

        except Exception as e:
            print(e)

# Trim text to MAX_LEN_QUOTED_TEXT but don't cut off any words
def myTrim(text):
    
    if (len(text) > MAX_LEN_QUOTED_TEXT):
        result = text[:MAX_LEN_QUOTED_TEXT]
        lastSpace = result.rfind(' ')
        result += result[:lastSpace] 
        result += " ..."
    else: 
        result = text

    return result

# create the folders for the group messages and media (attachments)
def createGroupFolders(groups, folder):

    global MediaSubFolder

    try:
        for group in groups:
            groupFolder = os.path.join(folder, group.slug)
            createFolder(groupFolder)
            mediaFolder = os.path.join(groupFolder, MediaSubFolder)
            createFolder(mediaFolder)

    except Exception as e:
        print(e)

# -----------------------------------------------------------------------------
#
# Format a Message object in Markdown
#
# Parameters:
#
#    - message - the message being converted to Markdown
#    - mediaSubFolder - where attachments are found
#
# -----------------------------------------------------------------------------
def getMarkdown(message, mediaSubFolder):

    global Strings
    global Language
    global people

    # #todo eventually pass these settings as an object
    global IncludeTimestamp
    global ColonAfterContext
    global IncludeQuote
    global TimeNameSeparate
    global IncludeReactions

    text = ""

    if (TimeNameSeparate):
        text += NEW_LINE + message.timeStr + NEW_LINE

    firstName = getFirstNameByNumber(message.phoneNumber, people)

    # don't include first name if Note-to-Self since I know who I am!
    if (not message.isNoteToSelf()):
        text += firstName

    if (not TimeNameSeparate and IncludeTimestamp):
        if (not message.isNoteToSelf()):
            text += " " + getStr(STR_AT) + " "
        text += message.timeStr

    if (ColonAfterContext):
        text += ":" 
        
    if (not TimeNameSeparate):
        text += NEW_LINE
    
    for attachment in message.attachments:
        text += attachment.generateLink()
    
    text += MD_QUOTE

    if (IncludeQuote and len(message.quote.text)):
    
        lengthOfQuotedText = len(message.quote.text)
        if (lengthOfQuotedText):
            text += MD_QUOTE + message.quote.authorName + ": "
            quotedText = message.quote.text
            if (lengthOfQuotedText > MAX_LEN_QUOTED_TEXT):
                quotedText = quotedText.quote.text[:MAX_LEN_QUOTED_TEXT]
                lastSpace = quotedText.rfind(' ')
                text += quotedText[:lastSpace] 
                text += " ..."
            else: 
                text += quotedText

            text += NEW_LINE + MD_QUOTE + NEW_LINE + MD_QUOTE

    if (len(message.body)):
        text += message.body + NEW_LINE

    if (IncludeReactions and len(message.reactions)):
        text += MD_QUOTE + NEW_LINE + MD_QUOTE
        for reaction in message.reactions:
            firstName = getFirstNameBySlug(reaction.sourceSlug)
            text += reaction.emoji + "*" + firstName.lower() + "*   "
        text += NEW_LINE

    text += NEW_LINE

    return text

# -----------------------------------------------------------------------------
#
# Grab the attachments meta data from the message.
# Parameters:
# 
#   - json - attachments metat data in JSON from the Signal output
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
    i = 0
    
    for data in jsonAttachments:
        try:
            attachment = Attachment()
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
            message.attachments.append(attachment)

        except:
            pass

        i += 1

    return i

# Lookup a message by it's timestamp (and author) and add the reaction to it
#
# Returns:
#
#    - True if the message was found
#    - False if the message was not found
#
def addReactionToMesssage(reaction):
    
    global messages

    result = False

    for message in messages:
        if (message.timeStamp == reaction.targetTimeSent):
            message.reactions.append(reaction)
            result = True
            break

    return result

# -----------------------------------------------------------------------------
#
# Read the message from JSON into a Message object
#
# Parameters:
#
#   - type - type of message, either JSON_SYNC_MESSAGE or JSON_DATA_MESSAGE
#   - line - the entire message contents
#   - people - collection of Person objects
#   - message - the target Message object where the values will go
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
def extractMessage(type, line, people, message):

    timeInSeconds = 0
    numAttachments = 0
    toPerson = Person()  
    author = Person()    # if a JSON_QUOTE in reply to the author

    data = line[JSON_DATA]
    
    try:
        message.phoneNumber = data[JSON_SOURCE][JSON_NUMBER]
        message.sourceUUID  = data[JSON_SOURCE][JSON_UUID]
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
   
    if (type == JSON_DATA_MESSAGE):
        jsonMessage = data[JSON_DATA_MESSAGE]
    elif (type == JSON_SYNC_MESSAGE):
        jsonSent = data[JSON_SYNC_MESSAGE][JSON_SENT]
        jsonMessage = jsonSent[JSON_MESSAGE]

        # the destination is not always present
        try:
            message.destinationUUID = jsonSent[JSON_DESTINATION][JSON_UUID]
            toPerson = getPersonByUUID(message.destinationUUID, people)
            message.destinationSlug = toPerson.slug
        except:
            pass

    try:
        message.body = jsonMessage[JSON_BODY]
    except:
        try:
            reaction = Reaction()
            source = getPersonByUUID(message.sourceUUID, people)
            reaction.sourceSlug = source.slug
            jsonReaction = jsonMessage[JSON_REACTION]
            reaction.emoji = jsonReaction[JSON_EMOJI]
            reaction.targetAuthorUUID = jsonReaction[JSON_TARGET_AUTHOR]
            reaction.targetTimeSent = jsonReaction[JSON_TARGET_SENT_TIMESTAMP]
            addReactionToMesssage(reaction)
        except Exception as e:
            pass

    # see if it's a reply
    try:
        theQuote = jsonMessage[JSON_QUOTE]
        message.quote.id = theQuote[JSON_QUOTE_ID]
        message.quote.authorUUID = theQuote[JSON_QUOTE_AUTHOR][JSON_UUID]
        message.quote.text = theQuote[JSON_QUOTE_TEXT]
        author = getPersonByUUID(message.quote.authorUUID, people)
        message.quote.authorName = author.firstName
        message.quote.authorSlug = author.slug
    except:
        pass

    # see if it's a group message
    try:
        group = jsonMessage[JSON_GROUPV2]
        groupId = group[JSON_GROUP_ID]
        message.groupSlug = getGroupSlug(groupId, groups)
    except:
        pass

    # see if it's an attachment
    try:
        jsonAttachments = jsonMessage[JSON_ATTACHMENTS]
        numAttachments = extractAttachmentData(jsonAttachments, message)
    except:
        pass
    
    if (len(message.phoneNumber)):
        person = getPersonByNumber(message.phoneNumber, people)
        person.uuid = message.sourceUUID
        message.sourceSlug = person.slug
    
    if (message.time):
        try:
            message.dateStr = time.strftime("%Y-%m-%d", message.time)
            message.timeStr = time.strftime("%H:%M", message.time)
        except Exception as exception:
            print(exception)

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
def processLine(line, people, message):

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

    if (len(account) and len(number)):
        if (account == number):
            extractMessage(JSON_SYNC_MESSAGE, line, people, message)
        else:
            extractMessage(JSON_DATA_MESSAGE, line, people, message)
        result = True

    return result

# parse a line from the signald JSON output file
def parseLine(theLine, people, message):

    result = False
    
    jsonMessage = json.loads(theLine)

    if (JSON_TYPE in jsonMessage):
        if (jsonMessage[JSON_TYPE] == JSON_INCOMING_MESSAGE):
            result = processLine(jsonMessage, people, message)

    return result

# go though each line of the source file and process it by loading each message
# into a `Message` object and adding it to the `Messages` collection
def loadMessages(fileName, messages):

    ignored = 0
    parsed = 0
    errored = 0
    noBodyOrAttachment = 0
    i = 0

    try:
        sourceFile = open(fileName, 'r', encoding="utf-8")
    except Exception as e:
        print(getStr(STR_COULD_NOT_OPEN_MESSAGES_FILE) + ": " + fileName)
        print(e)
        return i

    while True:
        line = ""

        try:
            line = sourceFile.readline()

            if not line:
                print(getStr(STR_FAILED_TO_READ_LINE))
                break

            line = line.encode("utf-8")
            line = line.rstrip()

            try:
                message = Message()
                if (parseLine(line, people, message)):
                    parsed += 1

                    if (len(message.body) or len(message.attachments)):
                        messages.append(message)
                    else:
                        noBodyOrAttachment +=1

            except Exception as exception1:
                errored += 1

        except Exception as exception2: 
            ignored += 1 # failed

        i += 1

    print("parsed: "  + str(parsed))
    print("errored: " + str(errored))
    print("no body or attachment: " + str(noBodyOrAttachment))
    print("ignored: " + str(ignored))

    sourceFile.close()

    return i

# add the messages to the group or person on the day they happened
def appendMessage(message, collection):

    dateFound = False

    # go through existing dates and add message there
    for messagesOnDate in collection.messages:
        if (message.dateStr == messagesOnDate.dateStr):
            dateFound = True
            messagesOnDate.messages.append(message)

    # if the date was not found, create it
    if (dateFound == False):
        newDate = DatedMessages()
        newDate.dateStr = message.dateStr
        newDate.messages.append(message)
        collection.messages.append(newDate)

# divy up the messages to the groups and people they were with, by day
def addMessages(messages, people, groups, mySlug):
    
    for message in messages:

        if (len(message.groupSlug)):

            for group in groups:
                if (message.groupSlug == group.slug):
                    appendMessage(message, group)
                    message.processed = True

        elif (len(message.sourceSlug)):
            for person in people:
                personSlug = person.slug
                sourceSlug = message.sourceSlug
                destinationSlug = message.destinationSlug

                if (message.processed == False and (person.slug != mySlug) 
                   and (sourceSlug == personSlug) or (destinationSlug == personSlug)):
                    appendMessage(message, person)
                    message.processed = True

    return

def getFrontMatter(message, mySlug):

    global groups
    
    frontMatter = YAML_DASHES 
    frontMatter += YAML_TAGS + ": [" + TAG_CHAT + "]" + NEW_LINE
    frontMatter += YAML_PERSON_SLUGS + ": [" + mySlug 

    if (len(message.destinationSlug) and message.destinationSlug != mySlug):
        frontMatter += ", " + message.destinationSlug
    
    elif (len(message.groupSlug)):
        for group in groups:
            if (group.slug == message.groupSlug):
                for personSlug in group.members:
                    frontMatter += ", " + personSlug
                break

    elif (len(message.sourceSlug) and message.sourceSlug != mySlug):
        frontMatter += ", " + message.sourceSlug

    frontMatter += "]" + NEW_LINE
    frontMatter += YAML_DATE + ": " + message.dateStr + NEW_LINE
    frontMatter += YAML_TIME + ": " + message.timeStr + NEW_LINE
    frontMatter += YAML_SERVICE_SLUG + ": " + YAML_SERVICE_SIGNAL + NEW_LINE
    frontMatter += YAML_DASHES + NEW_LINE

    return frontMatter

# -----------------------------------------------------------------------------
#
# Generate the output folder name.
#
# Notes
# 
#   - if it's a regular message, the folder will be the destination person slug
#   - if it's an attachment, the folder will be the source (sender)
#
# Parameters:
#
#   - entity: a Person or a Group object
#   - outputFolder: root folder where the subfolder per-person / files created
#   - message: the current message being processed
#   - mySlug: slug of the person who runs this tool
#
# -----------------------------------------------------------------------------
def getMediaFolderName(entity, outputFolder, message, mySlug):

    global DailyNotesFolder

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if type(entity) == Group:
        folder = os.path.join(outputFolder, entity.slug)
    elif message.isNoteToSelf() and len(DailyNotesFolder):
        folder = DailyNotesFolder
    elif message.hasAttachment() and message.sourceSlug == mySlug:
        folder = os.path.join(outputFolder, mySlug)
    else:
        folder = os.path.join(outputFolder, entity.slug)

    return folder

# -----------------------------------------------------------------------------
#
# Generate the output folder name.
#
# Notes
# 
#   - if it's a regular message, the folder will be the destination person slug
#
# Parameters:
#
#   - entity: a Person or a Group object
#   - outputFolder: root folder where the subfolder per-person / files created
#   - message: the current message being processed
#   - mySlug: slug of the person who runs this tool
#
# -----------------------------------------------------------------------------
def getMarkdownFolderName(entity, outputFolder, message, mySlug):

    global DailyNotesFolder

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if type(entity) == Group:
        folder = os.path.join(outputFolder, entity.slug)
    elif message.isNoteToSelf() and len(DailyNotesFolder):
        folder = DailyNotesFolder
    else:
        folder = os.path.join(outputFolder, entity.slug)

    return folder

# -----------------------------------------------------------------------------
#
# Generate the output filename
#
# Parameters:
#
#   - entity: a Person or a Group object
#   - outputFolder: root folder where the subfolder per-person / files created
#   - message: the current message being processed
#   - mySlug: slug of person that runs this tool
#
# -----------------------------------------------------------------------------
def getMarkdownFileName(entity, outputFolder, message, mySlug):

    folder = getMarkdownFolderName(entity, outputFolder, message, mySlug)
    fileName = os.path.join(folder, message.dateStr + OUTPUT_FILE_EXTENSION)
    
    return fileName

# -----------------------------------------------------------------------------
#
# Parameters:
#
#   - fileName - the file to open
#
# Returns a file handle
#
# -----------------------------------------------------------------------------
def openOutputFile(fileName):

    outputFile = False

    try:
        outputFile = open(fileName, 'a', encoding="utf-8")

    except Exception as exception:
        errorStr = getStr(STR_ERROR) + " " + getStr(STR_COULD_NOT_OPEN_FILE) + " " + str(exception)
        print(errorStr)

    return outputFile

# -----------------------------------------------------------------------------
#
# Create the Markdown
#
# Parameters:
#
#   - entity - a Person or a Group object
#   - outputFolder - root folder for the markdown files go
#   - mediaSubFolder - where the attachements go 
#   - mySlug - unique short label identifying myself in `people.json`
#
# -----------------------------------------------------------------------------
def createMarkdownFile(entity, outputFolder, mediaSubFolder, mySlug):

    exists = False
    
    for datedMessages in entity.messages:

        for message in datedMessages.messages:

            fileName = getMarkdownFileName(entity, outputFolder, message, mySlug)
            exists = os.path.exists(fileName) 
            outputFile = openOutputFile(fileName)

            if (outputFile):
                # add the front matter if this is a new file
                if (exists == False):
                    frontMatter = getFrontMatter(message, mySlug)
                    outputFile.write(frontMatter)
         
                try:
                    outputFile.write(getMarkdown(message, mediaSubFolder))
                    outputFile.close()
                except Exception as exception:
                    pass

# -----------------------------------------------------------------------------
#
# Parameters
# 
#   - collection - either people or groups
#   - outputFolder - where the files will go
#   - mySlug - short string identifying myself in `people.json`
#
# -----------------------------------------------------------------------------
def generateMarkdownFiles(collection, outputFolder, mediaSubFolder, mySlug):
    for item in collection:
        createMarkdownFile(item, outputFolder, mediaSubFolder, mySlug)
    return

# -----------------------------------------------------------------------------
#
# Move the attachments from the `signald-output` folder to the folder of the
# specific person that shared them. If it's a group message, move the 
# attachments under the `group` folder.
#
# Parameters
# 
#   - entities - either a collection of Person or Group objects
#   - outputFolder - top-level folder where the files will go
#   - subFolder - media folder to place the attachments
#   - mySlug - slug of the main person using the tool
# 
# -----------------------------------------------------------------------------
def moveAttachments(entities, outputFolder, subFolder, mySlug):

    global AttachmentsFolder
    global MIMETypes

    sourceFile = ""
    destFile = ""

    for entity in entities:
        for datedMessages in entity.messages:
            for message in datedMessages.messages:
                destFolder = getMediaFolderName(entity, outputFolder, message, mySlug)
                destFolder = os.path.join(destFolder, subFolder)
                for attachment in message.attachments:
                    if (len(attachment.id)):
                        sourceFile = os.path.join(AttachmentsFolder, attachment.id)
                        destFile = os.path.join(destFolder, attachment.withSuffix())

                        if os.path.exists(sourceFile) and not os.path.exists(destFile):
                            try: 
                                shutil.move(sourceFile, destFile)
                            except Exception as e:
                                print(getStr(STR_COULD_NOT_MOVE_THE_ATTACHMENT) + ": " + sourceFile + " -> " + destFile)
                                print(e)
# main

loadStrings()

loadSettings()

# maybe only show this in some verbose mode?
print(SETTING_LANGUAGE + ": " + str(Language))
print(SETTING_MY_SLUG + ": " + str(MySlug))
print(SETTING_SOURCE_FOLDER + ": " + SourceFolder)
print(SETTING_ATTACHMENTS_SUB_FOLDER + ": " + str(AttachmentsFolder))
print(SETTING_ARCHIVE_FOLDER + ": " + str(ArchiveFolder))
print(SETTING_OUTPUT_FOLDER + ": " + str(OutputFolder))
print(SETTING_MEDIA_SUBFOLDER + ": " + str(MediaSubFolder))
print(SETTING_IMAGE_EMBED + ": " + str(ImageEmbed))
print(SETTING_IMAGE_WIDTH + ": " + str(ImageWidth))
print(SETTING_FOLDER_PER_PERSON + ": " + str(FolderPerPerson))
print(SETTING_FILE_PER_PERSON + ": " + str(FilePerPerson))
print(SETTING_FILE_PER_DAY + ": " + str(FilePerDay))
print(SETTING_INCLUDE_TIMESTAMP + ": " + str(IncludeTimestamp))
print(SETTING_INCLUDE_REACTIONS + ": " + str(IncludeReactions))
print(SETTING_INCLUDE_QUOTE + ": " + str(IncludeQuote))
print(SETTING_COLON_AFTER_CONTEXT + ": " + str(ColonAfterContext))
print(SETTING_TIME_NAME_SEPARATE + ": " + str(TimeNameSeparate))
print(SETTING_DAILY_NOTES_FOLDER + ": " + str(DailyNotesFolder))

loadMIMETypes()

# make a copy of the source file for now. Later once everything works
# perfectly this will actually move it #todo
try:
    Path(ArchiveFolder).mkdir(parents=True, exist_ok=True)
    nowStr = datetime.strftime(datetime.now(), '%Y-%m-%d %H-%m-%S')
    fileName = "messages_" + nowStr + "." + MESSAGES_SUFFIX
    destFile = os.path.join(ArchiveFolder, fileName)
    try:
        shutil.move(MessagesFile, destFile)
    
        createFolder(DailyNotesFolder)
        createFolder(os.path.join(DailyNotesFolder, MediaSubFolder))

        loadPeople(people)
        createPersonFolders(people, OutputFolder, MySlug)

        loadGroups(groups)
        createGroupFolders(groups, GroupsFolder)

        messages = []
        if (os.path.exists(destFile) and loadMessages(destFile, messages)):
            addMessages(messages, people, groups, MySlug)
            moveAttachments(people, OutputFolder, MediaSubFolder, MySlug)
            moveAttachments(groups, GroupsFolder, MediaSubFolder, MySlug)
            generateMarkdownFiles(people, OutputFolder, MediaSubFolder, MySlug)
            generateMarkdownFiles(groups, GroupsFolder, MediaSubFolder, MySlug)

    except Exception as e:
        print(getStr(STR_COULD_NOT_MOVE_MESSAGES_FILE) + ": " + MessagesFile)
        print(e)

except Exception as e:
    print(getStr(STR_COULD_CREATE_ARCHIVE_FOLDER) + ": " + MessagesFile)
    print(e)