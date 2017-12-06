from oauth2client import client
import httplib2
from googleapiclient import discovery, http


def lambda_handler(event, context):  # function that is called when you say something to Alexa
    if event['session']['new']:
        pass
    if event['request']['type'] == "LaunchRequest":
        return LaunchRequest(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":  # our main point of interest!!!
        return IntentRequest(event['request'], event)
    elif event['request']['type'] == "SessionEndedRequest":
        return SessionEndedRequest(event['request'], event['session'])


def response(atts, outputtext,
             SES):  # this functions builds response in the correct format / outputtext==>What alexa says as a response
    return {
        "version": "1.0",
        "sessionAttributes": atts
        ,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": outputtext
            },
            "card": {
                "type": "Simple",
                "title": "",
                "content": ""
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": ""
                }
            },
            "shouldEndSession": SES
        }
    }


def LaunchRequest(eventrequest, session):  # this is called when you ask alexa to open the skill
    return response({}, "Hello, what would you like to do?", False)


def IntentRequest(eventrequest, event):
    token = event["session"]["user"][
        "accessToken"]  # access token coming in request, Alexa automatically refreshes it after one hour
    slotvalue = "nothing"
    if len(event["request"]["intent"]["slots"]["something"]) > 1:  # if the user specified the CONTENT of the file
        slotvalue = event["request"]["intent"]["slots"]["something"]["value"]
    if len(event["request"]["intent"]["slots"]["somethingTWO"]) > 1:
        slotvalue += " " + event["request"]["intent"]["slots"]["somethingTWO"][
            "value"]  # it is divided into two slots to be able to make whole sentences

    if slotvalue != "nothing": #user didnt specify the content. nothingDOC.txt is uploaded with content ’nothing’
        CreateFileWithContentAndUpload(str(slotvalue) + "DOC.txt", str(slotvalue), StartDrive(token), None)
    else:
        CreateFileWithContentAndUpload("RandomDOC.txt", "Random document", StartDrive(token), None)
    return response({}, "The file has been uploaded saying: " + slotvalue, False)


def SessionEndedRequest(eventrequest, session):
    return response({}, "In SessionEndedRequest", False)


def CreateFile(name,
               DRIVE):  # function that creates a file of a specified mimetype /txt, doc, png, jpg........ not used in this version, just defined
    file_metadata = {'name': name, 'mimeType': mimetype}
    file = DRIVE.files().create(body=file_metadata, fields='id').execute()
    print('File ID: %s' % file.get('id'))


def StartDrive(token):  # this initiates the DRIVE object to be called in other function
    credentials = client.AccessTokenCredentials(token,
                                                'my-user-agent/1.0')  # obtaining credentials from the accesstoken
    http = httplib2.Http()
    http = credentials.authorize(http)  # authentication of the user credentials
    DRIVE = discovery.build('drive', 'v3', http=http)  # making of the DRIVE object
    return DRIVE


def uploadToDrive(FILES, DRIVE):  # uploads already existing files from the current directory
    for name, mimeType in FILES:
        metadata = {"name": name}
        if mimeType:  # if mimetype is not specified, it is automatically generated ( .txt every time in this skill(left here for future scaling))
            metadata["mimeType"] = mimeType
        res = DRIVE.files().create(body=metadata, media_body=name).execute()
        if res:
            print("Uploaded %s to Drive" % name)


def CreateFileWithContentAndUpload(name, content, DRIVE, mimetype):
    f = open("/tmp/" + name, 'w')  # creates file
    f.write(content)  # writes some content into it
    f.close()
    FILE = {("/tmp/" + name, None)}
    uploadToDrive(FILE, DRIVE)  # uploads it








