########################################################################################################
#
#  main.py - for spike version of Google Cloud Function to take a data item
#            representing a candidate Rally PullRequest off of a
#            Google PubSub topic (via specific subscription) and use the Rally WSAPI
#            to create said PullRequest in the Rally system.
#            Requires an APIKey to be part of the incoming payload envelope,
#            and requires a call to Rally WSAPI to confirm the presence of a mentioned
#            Rally Artifact URL (FDP oriented URL) in the message.
#            The confirmation is necessary to pull out the Workspace ref info which
#            in turn is used to augment the candidate Rally PullRequest payload.
#
########################################################################################################

import sys
import time
import json
import base64

import requests

########################################################################################################

BASE_RALLY_URL  = 'https://rally1.rallydev.com/slm/webservice/v2.0'
XMIT_ATTEMPT_BACKOFFS = [2.5, 7, 0]

########################################################################################################

def parsePullRequest(data, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         data (dict): The dictionary with data specific to this type of event.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata.
    """
    import base64

    if 'data' in data:
        name = base64.b64decode(data['data']).decode('utf-8')
    else:
        name = 'World'
    print('Hello {}!'.format(name))

def createRallyPullRequest(data, context):
    """
        Background Cloud Function to be triggered by Pub/Sub.
           Args:
              data (dict): The dictionary with data specific to this type of event.
              context (google.cloud.functions.Context): The Cloud Functions event metadata.
    """
    if 'data' not in data:
       raise Exception("Unexpected data package, no 'data' key found in payload")

    try:
        message = base64.b64decode(data['data']).decode('utf-8')
    except Exception as exc:
        sys.stderr.write("%s: Unable to decode via base64 this value: %s\n" % (exc[0], data['data']))
        sys.exit(3)
    try:
        message = json.loads(message)
    except Exception as exc:
        sys.stderr.write("%s: Unable to JSON xlate to Python dict this string: %s\n" % (exc[0], message))
        sys.exit(4)

    apikey  = message["APIKey"]
    payload = message["PullRequest"]

    for backoff in XMIT_ATTEMPT_BACKOFFS:
        workspace_ref = getArtifactWorkspaceRef(payload, apikey)
        payload['Workspace'] = workspace_ref
        rally_pull_request, reason = postPullRequest(payload, apikey)
        if rally_pull_request:
            break

        if 'concurrency' in reason.lower():
            if backoff:
                print(f"will retry create PullRequest attempt in {backoff}, {reason}")
            else:
                sys.stderr.write("unable to create PullRequest for %s after 3 attempts\n" % rally_pull_request['ExternalID'])
            time.sleep(backoff)
        else:
            break

###################################################################################################

def postPullRequest(payload, apikey):
    headers = {'zsessionid' : apikey}
    pr_create = "pullrequest/create"
    pr_create_endpoint = f"{BASE_RALLY_URL}/{pr_create}"
    try:
        response = requests.post(pr_create_endpoint, headers=headers, data=json.dumps(payload))
        if response.text.startswith('<html>') and response.text.endswith('</html>'):
            print("response is HTML, not JSON data.  Here is the content")
            print(response.text)
            return False, "response is not JSON data"
        response = response.json()
    except requests.exceptions.RequestException as exc:
        print(exc)
        return False, "%s: %s" % (exc[0], exc[1])
    return response, None


def getArtifactWorkspaceRef(payload, apikey):
    headers = {'zsessionid' : apikey}
    artifact_ref = payload['Artifact']
    #print("artifact_ref before split: %s" % artifact_ref)
    temp, short_ref = artifact_ref.split('/#/detail/', 1)
    if 'userstory' in short_ref:
        short_ref = short_ref.replace('userstory', 'hierarchicalrequirement')
    url = f'{BASE_RALLY_URL}/{short_ref}'
    try:
        response = requests.get(url, headers=headers)
        #print("getArtifactWorkspaceRef response: %s" % response.text)
        message_dict = json.loads(response.text)
    except Exception as exc:
        sys.stderr.write("%s: unable to query Rally for specific Artifact: %s\n" % (exc[0], short_ref))
        sys.exit(2)
    workspace = message_dict['HierarchicalRequirement']['Workspace']['_ref']
    return workspace

