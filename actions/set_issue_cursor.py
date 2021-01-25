# Copyright (c) 2021, DCSO GmbH

import sys

from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from lib.helpers import get_key_client


class SetIssueCursor(Action):
    def run(self, value):
        try:
            key_client = get_key_client()

            if value is None:
                value = ""

            key_client.keys.update(KeyValuePair(name='dcso.issue_cursor', value=value))
            print("Success", end="")
        except:
            print("Failure", end="")
            sys.exit(1)
