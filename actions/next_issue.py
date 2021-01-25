# Copyright (c) 2021, DCSO GmbH

from dcso.portal import PortalException
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from lib.helpers import get_issue_url, get_key_client, get_api_client


class NextIssue(Action):
    def run(self):
        api_url = self.config.get('api_uri')
        key_client = get_key_client()
        api_token = key_client.keys.get_by_name(name="dcso.api_token", decrypt=True).value
        cursor = key_client.keys.get_by_name(name='dcso.issue_cursor')
        if cursor:
            cursor = cursor.value
        else:
            cursor = ""

        client = get_api_client(api_url=api_url, api_token=api_token)

        q = """query($cursor: Cursor)
               {
                 issues(first:1 after:$cursor)  {
                   edges {
                     cursor
                     node {
                       id
                       reference
                       summary
                       status
                       ...on AlertIssue {
                         alertsFrom
                         alertsTill
                         taxonomy { urgency { key value } impact { key value }}
                         recommendation
                         alertClassification { alertLabels }
                       }
                     }
                   }
                 }
               }
            """

        variables = {
            'cursor': cursor
        }

        result = {"status": "FAILED", "node": None}
        try:
            response = client.execute_graphql_dict(query=q, variables=variables)
            issues = response["issues"]["edges"]
            result["status"] = "SUCCESS"
            if len(issues) > 0:
                new_cursor = issues[0]["cursor"]
                key_client.keys.update(KeyValuePair(name='dcso.issue_cursor', value=new_cursor))
                result["node"] = issues[0]["node"]
                issue_url = get_issue_url(api_client=client, issue_id=issues[0]["node"]["id"])
                result["node"]["portalUrl"] = issue_url
        except PortalException as exc:
            result["error"] = str(exc)

        return result
