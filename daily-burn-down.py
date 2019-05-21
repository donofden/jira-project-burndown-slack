#!/usr/bin/python
##
# CLI script to retrieving data from JIRA
##
import requests
import argparse
import sys
import pandas as pd
from decimal import *
from tabulate import tabulate


class DailyBurnDown:

    url = ''
    token = ''
    jira_url = 'YOUR_ORGANIZATION_JIRA_URL.atlassian.net'

    @staticmethod
    def get_arg_parser():
        """ Creates an ArgumentParser to parse the command line options. """

        parser = argparse.ArgumentParser(
            description='Calculate burn down for the Day from JIRA'
        )
        parser.add_argument('-a', '--token', help='Authorization Token to JIRA Board')

        return parser


    def call_api(self):
        """ Call API to fetch details from the given URL """
        # http://docs.python-requests.org/en/latest/user/advanced/#session-objects
        session_with_header = requests.Session()
        session_with_header.headers.update({'Authorization': 'Basic '+self.token})
        # request and saving the response as object
        response = session_with_header.get(self.url)

        # Check API Response
        if response.status_code == 200:
            return response.json()
        else:
            print("API Failure")
            sys.exit(1)


    def get_team_board(self):
        """ Get the current iteration id as per Azure DevOps config """

        start_pagination = 0
        max_record = 50
        rapidview_id = ''
        # Get Current Iteration
        # Since Jira Paginates the API output we are looping through all the value to find Current Iteration
        while True:
            self.url = 'https://'+self.jira_url+'/rest/agile/latest/board?startAt='+str(start_pagination)+'&maxResults=50'
            json_object = self.call_api()
            if json_object['total'] > start_pagination:
                start_pagination = start_pagination + max_record
            if len(json_object['values']) == 0:
                break
            for boards in json_object['values']:
                # Get the current Board ID i.e sored in rapidview_id
                if boards['name'] == "Internal Systems " and boards['type'] == "scrum":
                    rapidview_id = boards['id']

        self.url = 'https://'+self.jira_url+'/rest/greenhopper/latest/sprintquery/'+str(rapidview_id)+'?includeHistoricSprints=true'

        json_object = self.call_api()
        for sprint_boards in json_object['sprints']:
            # Get the Active Sprint ID
            if sprint_boards['state'] == "ACTIVE":
                sprint_id = sprint_boards['id']

        self.url = 'https://'+self.jira_url+'/rest/greenhopper/latest/rapid/charts/sprintreport?rapidViewId='+str(rapidview_id)+'&sprintId='+str(sprint_id)
        json_object = self.call_api()
        allowed_status = ["completedIssues", "issuesNotCompletedInCurrentSprint", "puntedIssues"]
        allowed_type = ["Bug", "Story"]
        board_dict = {}

        for status in json_object['contents']:
            if status in allowed_status:
                for cards in json_object['contents'][status]:
                    if cards['typeName'] in allowed_type:
                        for story_point_value in cards['estimateStatistic']:
                            if 'statFieldValue' == story_point_value:
                                storypoint = 0.0
                                if "value" in cards['estimateStatistic'][story_point_value]:
                                    storypoint = cards['estimateStatistic'][story_point_value]['value']
                                    board_column = cards['statusName']
                                    # Prepare the Output Dict
                                    if board_column in board_dict:
                                        new_value = float(board_dict[board_column].get('point')) + float(storypoint)
                                        no_of_card = board_dict[board_column].get('items') + 1
                                        board_dict[board_column] = {'point': new_value, 'items': no_of_card}
                                    else:
                                        board_dict[board_column] = {'point': storypoint, 'items': 1}

        # Format the output
        df = pd.DataFrame(board_dict)
        df = df.T
        df.columns = ["items", "points"]
        df = df.astype(int)
        df.loc["TOTAL"] = df.sum().T
        print(tabulate(df, headers="keys", tablefmt="rst"))

    def run(self):
        """ Main application entry point """

        parser = self.get_arg_parser()
        arguments = parser.parse_args()
        if not all([arguments.token]):
            parser.print_help()
            sys.exit(1)
        else:
            self.token = arguments.token
            self.get_team_board()


if __name__ == '__main__':
    b = DailyBurnDown()
    b.run()
