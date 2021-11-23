# Copyright (c) 2021, DCSO GmbH

import json
from dcso.portal import APIClient
from st2client.models.core import ResourceManager
from st2tests.base import BaseActionTestCase
from st2tests.mocks.action import MockActionWrapper, MockActionService
from unittest.mock import patch
from actions.next_issues import NextIssues


class NextIssuesActionTestCase(BaseActionTestCase):
    action_cls = NextIssues
    action_wrapper = MockActionWrapper(pack='dcso', class_name=action_cls.__name__)
    action_service = MockActionService(action_wrapper=action_wrapper)

    class KeyMock:
        value = None

    def setUp(self):
        self.maxDiff = None
        self.issues_graphql_response = json.loads(self.get_fixture_content("next_issues_api_response.json"))
        self.tdh_issue_graphql_response = json.loads(self.get_fixture_content("tdh_issue_api_response.json"))
        self.next_issues_plugin_response = json.loads(self.get_fixture_content("next_issues_plugin_response.json"))
        self.key_client = NextIssuesActionTestCase.KeyMock()

    @patch.object(APIClient, 'execute_graphql_dict')
    @patch("dcso.portal.APIClient.api_url")
    @patch.object(ResourceManager, 'update')
    @patch.object(ResourceManager, 'get_by_name')
    def test_next_issues(self, mock_get_key, mock_update_key, mock_api_url, mock_graphql):
        action = self.get_action_instance(config={'portal_uri': 'https://test.url'})
        # mock key_client/key-value store
        mock_get_key.return_value = self.key_client
        mock_update_key.return_value = None
        # mock api_url for APIClient
        mock_api_url.return_value = "test.url"
        # mock graphql responses for 'issues' query and 'tdh_issue' query
        mock_graphql.side_effect = [self.issues_graphql_response] + 2*[self.tdh_issue_graphql_response]
        # run action -> next_issue
        result = action.run(2)
        expected = self.next_issues_plugin_response
        self.assertEqual(result, expected)
