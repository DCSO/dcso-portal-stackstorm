# Copyright (c) 2021, DCSO GmbH

from dcso.portal import PortalException
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from lib.helpers import get_issue_url, get_key_client, get_api_client


class NextIssues(Action):
    def run(self, number_of_issues):
        api_url = self.config.get('api_uri')
        key_client = get_key_client()
        api_token = key_client.keys.get_by_name(name="dcso.api_token", decrypt=True).value
        cursor = key_client.keys.get_by_name(name='dcso.issue_cursor')
        if cursor:
            cursor = cursor.value
        else:
            cursor = ""

        client = get_api_client(api_url=api_url, api_token=api_token)

        q = """query($cursor: Cursor, $amount: Int)
               {
                 issues(first:$amount after:$cursor)  {
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
                    pageInfo{
                    hasNextPage
                    endCursor
                 }
                 }
               }
            """

        variables = {
            'cursor': cursor,
            'amount': number_of_issues
        }

        results = []
        try:
            response = client.execute_graphql_dict(query=q, variables=variables)
            issues = response["issues"]["edges"]
            if len(issues) > 0:
                results = {"status": "SUCCESS", "nodes": []}
                for issue in issues:
                    # append issue to list
                    issue_url = get_issue_url(api_client=client, issue_id=issue["node"]["id"])
                    issue["node"]["portalUrl"] = issue_url
                    results["nodes"].append(issue["node"])
                # update Cursor
                page_info = response["issues"].get("pageInfo")
                new_cursor = page_info.get("endCursor")
                key_client.keys.update(KeyValuePair(name='dcso.issue_cursor', value=new_cursor))
            else:
                results.append({"status": "SUCCESS", "nodes": None})
        except PortalException as exc:
            results.append({"status": "FAILED", "nodes": None, "error": str(exc)})

        return results
