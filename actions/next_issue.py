# Copyright (c) 2021, DCSO GmbH

from dcso.portal import PortalException
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from lib.helpers import get_issue_url, get_key_client, get_api_client, convert_timestamps_to_str, get_query_string


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

        q = get_query_string()

        variables = {
            'cursor': cursor,
            'amount': 1
        }

        result = {"status": "FAILED", "node": None}
        try:
            response = client.execute_graphql_dict(query=q, variables=variables)
            issues = response["issues"]["edges"]
            result["status"] = "SUCCESS"
            if len(issues) > 0:
                page_info = response["issues"].get("pageInfo")
                new_cursor = page_info.get("endCursor")
                key_client.keys.update(KeyValuePair(name='dcso.issue_cursor', value=new_cursor))
                result["node"] = convert_timestamps_to_str(issues[0]["node"])
                issue_url = get_issue_url(client, issues[0]["node"]["id"], self.config.get("portal_uri"))
                result["node"]["portalURL"] = issue_url
        except PortalException as exc:
            result["error"] = str(exc)

        return result
