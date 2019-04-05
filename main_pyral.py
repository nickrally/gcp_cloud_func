import sys
import requests
import time
import json
import base64

def createPullRequest(payload, apikey):
    artifact_ref = payload['Artifact']
    rally = Rally("rally1.rallydev.com", apikey=apikey)
    artifact = rally.get('Artifact', query='ObjectID = %s' % artifact_ref.split('/')[-1], instance=True)
    workspace = artifact.Workspace.Name
    try:
        rally_pull_request = rally.create('PullRequest', payload, workspace=workspace, project=None)
        print("Created PullRequest with ObjectID: %s" % rally_pull_request.oid)
    except RallyRESTAPIError as ex:
        #raise Exception("Could not create PullRequest  %s" % ex.args[0])
        print("Attempt to create a Rally PullRequest resulted in a %s" % ex.args[0])
        return None, ex.args[0]
    except Exception as ex:
        return None, ex.args[0]
    return rally_pull_request, "Success"


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

        for backoff in [2.5, 7, 0]:
            rally_pull_request, reason = createPullRequest(payload, apikey)
            if rally_pull_request:
                break
            elif 'concurrency' in reason.lower():
                if backoff:
                    print("will retry create PullRequest attempt in %s, %s" % (backoff, reason))
                else:
                    sys.stderr.write("unable to create PullRequest for %s after 3 attempts\n" % rally_pull_request['ExternalID'])
                time.sleep(backoff)
            else:

                break
        #print('DONE {}!'.format(rally_pull_request))

#
# def main(args):
#     global MESSAGE
#     payload = base64.encodebytes(MESSAGE.encode())
#     pub_sub_data = {'data' : payload}
#     createRallyPullRequest(pub_sub_data, None)
#
#
# if __name__ == "__main__":
#     main(sys.argv[1:])