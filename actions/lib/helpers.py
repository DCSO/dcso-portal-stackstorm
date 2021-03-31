# Copyright (c) 2021, DCSO GmbH

import os
from urllib.parse import urljoin

from dcso.portal import APIClient, PortalAPIError
from st2client.client import Client

ST2_ACTION_API_URL = os.environ.get('ST2_ACTION_API_URL')
ST2_ACTION_AUTH_TOKEN = os.environ.get('ST2_ACTION_AUTH_TOKEN')


def get_api_client(api_url, api_token):
    client = APIClient(api_url=api_url)
    client.token = api_token
    return client


def get_key_client():
    return Client(base_url=ST2_ACTION_API_URL, token=ST2_ACTION_AUTH_TOKEN)


def get_issue_url(api_client, issue_id, portal_url):
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
            url = urljoin(portal_url, f"tdh/issues/{issue_id}")
    except PortalAPIError:
        pass

    return url


def convert_timestamps_to_str(dictionary: dict) -> dict:
    for k, v in dictionary.items():
        try:
            dictionary[k] = v.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except AttributeError:
            pass
    return dictionary


def get_query_string():
    return """
            query($cursor: Cursor, $amount: Int)
               {
                 issues(first:$amount after:$cursor)  {
                   edges {
                     node {
                       ... on AlertIssue {
                         id
                         reference
                         organizationUID
                         summary
                         activeFrom
                         activeTill
                         alertsFrom
                         alertsTill
                         recommendation
                         taxonomy {
                           impact
                           urgency
                         }
                         sightings {
                           source
                           sourceData
                           attack {
                             name
                             description
                             urls
                           }
                         }
                         affectedEntities {
                           ...on SensorEntity {
                             id
                             value
                             type
                             role
                             state
                             comment
                             enrichment {
                               data
                               type
                               comment
                              }
                            }
                          }
                       }
                     }
                   }
                     pageInfo{
                     hasNextPage
                     endCursor
                   }
                 }
               }
            """
