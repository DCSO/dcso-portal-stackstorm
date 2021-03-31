# Copyright (c) 2021, DCSO GmbH

from dcso.portal import PortalException
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from lib.helpers import get_issue_url, get_key_client, get_api_client, convert_timestamps_to_str, get_query_string


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

        q = get_query_string()

        variables = {
            'cursor': cursor,
            'amount': number_of_issues
        }

        try:
            response = client.execute_graphql_dict(query=q, variables=variables)
            issues = response["issues"]["edges"]
            if len(issues) > 0:
                results = {"status": "SUCCESS", "nodes": []}
                for issue in issues:
                    # append issue to list
                    issue_url = get_issue_url(client, issue["node"]["id"], self.config.get("portal_uri"))
                    issue["node"]["portalURL"] = issue_url
                    results["nodes"].append(convert_timestamps_to_str(issue["node"]))
                # update Cursor
                page_info = response["issues"].get("pageInfo")
                new_cursor = page_info.get("endCursor")
                key_client.keys.update(KeyValuePair(name='dcso.issue_cursor', value=new_cursor))
            else:
                results = {"status": "SUCCESS", "nodes": None}
        except PortalException as exc:
            results = {"status": "FAILED", "nodes": None, "error": str(exc)}

        return results
