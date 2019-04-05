import sys
import time
import requests
import json
import base64

# def createPullRequest(payload, apikey):
#     artifact_ref = payload['Artifact']
#     rally = Rally("rally1.rallydev.com", apikey=apikey)
#     artifact = rally.get('Artifact', query='ObjectID = %s' % artifact_ref.split('/')[-1], instance=True)
#     workspace = artifact.Workspace.Name
#     try:
#         rally_pull_request = rally.create('PullRequest', payload, workspace=workspace, project=None)
#         print("Created PullRequest with ObjectID: %s" % rally_pull_request.oid)
#     except RallyRESTAPIError as ex:
#         #raise Exception("Could not create PullRequest  %s" % ex.args[0])
#         print("Attempt to create a Rally PullRequest resulted in a %s" % ex.args[0])
#         return None, ex.args[0]
#     except Exception as ex:
#         return None, ex.args[0]
#     return rally_pull_request, "Success"

# link = 'https://rally1.rallydev.com/#/detail/userstory/85293024712'
# temp, short_ref = link.split('/#/detail', 1)
# if 'userstory' in short_ref:
#     short_ref = short_ref.replace('userstory', 'hierarchicalrequirement')
# print(short_ref)
# base_url = 'https://rally1.rallydev.com/slm/webservice/v2.0'
# url      = '%s/%s' % (base_url, short_ref)

# headers = {'zsessionid':'_abc'}
# r = requests.get(url, headers=headers)
# print(r.status_code)
# print(r.text)
# print(type(r.text))
# d = json.loads(r.text)
# print(type(d))
# print(d.keys())

def post(self, payload):
    try:
        response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload))
        response = response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    return response

def createPullRequest(payload, apikey):
    artifact_ref = payload['Artifact']
    temp, short_ref = artifact_ref.split('/#/detail', 1)
    if 'userstory' in short_ref:
        short_ref = short_ref.replace('userstory', 'hierarchicalrequirement')
    # print(short_ref)
    base_url = 'https://rally1.rallydev.com/slm/webservice/v2.0'
    url      = '%s/%s' % (base_url, short_ref)
    headers = {'zsessionid':apikey} # nick@denver
    response = requests.get(url, headers=headers)
    d = json.loads(response.text)
    workspace = d['HierarchichalRequirement']['Workspace']['_ref']

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