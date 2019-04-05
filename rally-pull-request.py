def constructPullRequestPayload(pull_request, artifact):
    pr = pull_request
    payload = {
        'ExternalID'           : pr.ident,
        'ExternalFormattedId'  : pr.number,
        'Url'                  : pr.url,
        'Name'                 : pr.title,
        'Description'          : pr.description,
        'Artifact'             : artifact.ref
    }

    return payload

def validatedArtifacts(commit_fid):
    # commit_fid is a dict
    # commit_fid = {commitID: [S123,DE123], ...}
    try:
        fids = list(set([fid for fids in commit_fid.values() for fid in fids]))
    except Exception as msg:
        problem = "Cannot get a list of formatted ids of artifacts in the commit messages, in validatedArtfacts"
        raise OperationalError(problem)
    query = makeOrQuery("FormattedID", fids)
    response = rally.get('Artifact', fetch="FormattedID,ObjectID", query=query, project=None, pagesize=200, start=1)
    found_arts = [art for art in response]
    va = {}
    for ident in commit_fid.keys():
        va[ident] = []
        matches = [found_art for found_art in found_arts if found_art.FormattedID in commit_fid[ident]]
        if matches:
            va[ident] = matches
    return va


def identifyValidArtifacts(pull_request):
    """
        Look for valid artifact FormattedIDs in the commit messages AND in the
        title for the PullRequest.  Shove the PullRequest title value in to the
        list of commit messages so that is also considered.
    """
    commit_messages = pull_request.extractCommitMessages()
    commit_messages.insert(0, pull_request.title)
    related_fids = [{pull_request.ident: self.parseForArtifacts(commit_message)} for commit_message in
                    commit_messages]
    # wash out any items in related_fids that have an empty list for fids
    related_fids = [item for item in related_fids for value in item.values() if value]
    fid_list = []
    [fid_list.extend(element.values()) for element in related_fids]
    fids = [item for sublist in fid_list for item in sublist]
    if not fids:
        return []
    artifacts = validatedArtifacts({pull_request.ident: fids})[pull_request.ident]
    return artifacts


def createPullRequests(self, unrecorded_pull_requests):
    ac_pull_requests = []
    skipped_pull_requests = []
    for pull_request in unrecorded_pull_requests:
        artifacts = self.identifyValidArtifacts(pull_request)
        if not artifacts:
            skipped_pull_requests.append(pull_request.ident)
        for artifact in artifacts:
            if self.pullRequestExists(pull_request.ident, artifact):
                continue
            pr_payload = self.constructPullRequestPayload(pull_request, artifact)

            try:
                ac_pull_request = self.agicen.create('PullRequest', pr_payload)
                self.log.debug("    Created PullRequest in AgileCentral for  %s (%s)" % (
                ac_pull_request.Url, artifact.FormattedID))
                ac_pull_requests.append(ac_pull_request)
            except RallyRESTAPIError as ex:
                raise OperationalError("Could not create PullRequest  %s" % ex.args[0])

    return ac_pull_requests, skipped_pull_requests