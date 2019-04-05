import sys, os
import requests
import json
import base64

ARTIFACT_LINK = 'https://rally1.rallydev.com/#/detail/userstory/85293024712'
MESSAGE = '{"PullRequest": {"Url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347", "ExternalFormattedId": 1347, "Name": "new-feature", "Description": "Please pull these awesome changes for https://rally1.rallydev.com/#/detail/userstory/85293024712", "ExternalID": "e5bd3914e2e596debea16f433f57875b5b90bcd6"}, "SubscriptionID": 209, "APIKey": "%s", "GHMsgID": 19842471}' %os.getenv('APIKEY', None)


def createPullRequest(payload, apikey):
    temp, short_ref = ARTIFACT_LINK.split('/#/detail', 1)
    if 'userstory' in short_ref:
        short_ref = short_ref.replace('userstory', 'hierarchicalrequirement')
    base_url = 'https://rally1.rallydev.com/slm/webservice/v2.0'
    url      = '%s%s' % (base_url, short_ref)
    headers = {'zsessionid':apikey}
    response = requests.get(url, headers=headers)
    d = json.loads(response.text)
    workspace = d['HierarchicalRequirement']['Workspace']['_ref']
    payload['Workspace'] = workspace
    payload['Artifact']  = url
    pr = {}
    pr['PullRequest'] = payload
    try:
        #response = requests.post(base_url, headers=headers, data=json.dumps(payload))
        pr_create_endpoint = "%s%s" %(base_url,"/pullrequest/create")
        #response = requests.post(pr_create_endpoint, headers=headers, data=payload)
        #response = requests.post(pr_create_endpoint, headers=headers, data=json.dumps(payload))
        response = requests.post(pr_create_endpoint, headers=headers, json=pr)
        response = response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    return response


def createRallyPullRequest(data, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         data (dict): The dictionary with data specific to this type of event.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata.
    """


    if 'data' in data:
        message = base64.b64decode(data['data']).decode('utf-8')
        message = json.loads(message)
        apikey  = message["APIKey"]
        payload = message["PullRequest"]
        rally_pull_request = createPullRequest(payload, apikey)
        print('DONE {}!'.format(rally_pull_request))
        return rally_pull_request
    return None


def main(args):
    global MESSAGE
    payload = base64.encodebytes(MESSAGE.encode())
    pub_sub_data = {'data' : payload}
    pr = createRallyPullRequest(pub_sub_data, None)


if __name__ == "__main__":
    main(sys.argv[1:])