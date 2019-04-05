import sys, os
from pyral import Rally, RallyRESTAPIError
import json
import base64

MESSAGE = '{"PullRequest": {"Url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347", "ExternalFormattedId": 1347, "Name": "new-feature", "Description": "Please pull these awesome changes for https://rally1.rallydev.com/#/detail/userstory/85293024712", "ExternalID": "e5bd3914e2e596debea16f433f57875b5b90bcd6", "Artifact": "https://rally1.rallydev.com/slm/webservice/v2.0/hierarchicalrequirement/85293024712"}, "SubscriptionID": 209, "APIKey": "%s", "GHMsgID": 19842471}' %os.getenv('APIKEY',None)


def createPullRequest(payload, apikey):
    artifact_ref = payload['Artifact']
    rally = Rally("rally1.rallydev.com", apikey=apikey)
    artifact = rally.get('Artifact', query='ObjectID = %s' % artifact_ref.split('/')[-1], instance=True)
    workspace = artifact.Workspace.Name
    try:
        rally_pull_request = rally.create('PullRequest', payload, workspace=workspace, project=None)
        print("Created PullRequest with ObjectID: %s" % rally_pull_request.oid)
    except RallyRESTAPIError as ex:
        raise Exception("Could not create PullRequest  %s" % ex.args[0])
    return rally_pull_request



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


def main(args):
    global MESSAGE
    payload = base64.encodebytes(MESSAGE.encode())
    pub_sub_data = {'data' : payload}
    createRallyPullRequest(pub_sub_data, None)


if __name__ == "__main__":
    main(sys.argv[1:])