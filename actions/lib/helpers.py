# Copyright (c) 2021, DCSO GmbH

import os
from st2client.client import Client
from dcso.portal import APIClient, PortalAPIError

ST2_ACTION_API_URL = os.environ.get('ST2_ACTION_API_URL')
ST2_ACTION_AUTH_TOKEN = os.environ.get('ST2_ACTION_AUTH_TOKEN')


def get_api_client(api_url, api_token):
    client = APIClient(api_url=api_url)
    client.token = api_token
    return client


def get_key_client():
    return Client(base_url=ST2_ACTION_API_URL, token=ST2_ACTION_AUTH_TOKEN)


def get_issue_url(api_client, issue_id):
    q = """query ($id: String){
                tdh_issue(filter: {id: $id}) {
                    id
                    isPublished
                }
            }
        """

    variables = {
        'id': issue_id
    }

    url = None
    try:
        response = api_client.execute_graphql_dict(query=q, variables=variables)
        issue = response["data"]["tdh_issue"]
        if issue and issue.get("isPublished"):
            url = "https://portal.dcso.de/tdh/issues/{}".format(issue_id)
    except PortalAPIError:
        pass

    return url
