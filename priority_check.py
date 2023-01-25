"""
Priority Check
----------------------------
Written by dp24
----------------------------
Script checks for tickets in Decon

Reads their associated Yaml and looks for Priority flag

If not found then it defaults to low.

If found it will be changed to the relevant priority.

Runs in a test (doesn't change ticket) and
prod (changes ticket)

----------------------------
Usage:

Below env has the JIRA python module required.

/software/grit/conda/envs/Damon_project/bin/python3 priority_check.py test
"""

import os
import re
import sys
from jira import JIRA
from dotenv import load_dotenv

def dotloader():
    load_dotenv()
    return os.getenv('JIRA_USER'), os.getenv('JIRA_PASS'), os.getenv('JIRA_INST')

def authorise(url, user, password):
    return JIRA(url, basic_auth=(user, password))

def get_decon_list(auth):           
    return auth.search_issues(f'project IN ("ToL Assembly curation", "ToL Rapid Curation") AND labels = BlobToolKit AND status IN (curation,"Curation QC", Submitted, "In Submission")',
                            maxResults=10000)

def get_priorities(auth, list_of_tickets):
    dict_of_priorities = {}

    for i in list_of_tickets:
        priority = str(auth.issue(f'{i}').fields.priority)
        dict_of_priorities[str(i)] = { 'current': priority }

    return dict_of_priorities

def parse_yaml(auth, ticket):
    i = auth.issue(f'{ticket}')
    for attachment in i.fields.attachment:
        if str(attachment).startswith(i.fields.customfield_11627) and str(attachment).endswith('.yaml'):
            yaml_contents = "Content: '{}'".format(attachment.get())
        else:
            yaml_contents = 'NA'
    return yaml_contents

def parse_priority_yaml(auth, contents, ticket):
    priority = re.match(r"priority: (high|medium|low|lowest)", contents)
    if priority:
        return priority
    elif auth.issue(f'{ticket}').fields.priority:
        return auth.issue(f'{ticket}').fields.priority
    else:
        return 'low'

def set_new_priority(auth, ticket, priority):
    auth.issue(f'{ticket}').update(fields={'priority': f'{priority}'})

def main():
    new_priorities = {}
    filtered_list = []

    print("Starting search for priority tickets\nScript set to: {sys.argv[1]}")
    user, password, inst = dotloader()
    print(f"Logging in as: {user}")
    auth_jira = authorise(inst, user, password)
    list_of_tickets = get_decon_list(auth_jira)
    for i in list_of_tickets:
        print(f"{i} --- {auth_jira.issue(f'{i}').fields.summary}")
        project_check = str(auth_jira.issue(f'{i}').fields.summary)
        if 'ERGA' in project_check:
            new_priorities[str(i)] = 'Highest'
            print('ERGA')
        elif 'VGP' in project_check or 'GenomeArk' in project_check:
            new_priorities[str(i)] = 'Highest'
            print('GENOMEARK')
        elif 'faculty' in project_check:
            new_priorities[str(i)] = 'Highest'
            print('FACULTY')
        else:
            print('DARWIN OR OTHER')
            filtered_list.append(str(i))

    if len(filtered_list) >= 1:
        dict_of_priorities = get_priorities(auth_jira, filtered_list)
        for x, y in dict_of_priorities.items():
            print(str())
            contents = parse_yaml(auth_jira, x)
            new_priority = parse_priority_yaml(auth_jira, contents, x)
            if y['current'] == new_priority:
                pass
            else:
                new_priorities[str(x)] = new_priority
    else:
        sys.exit()

    for xx, yy in new_priorities.items():
        if sys.argv[1] == 'test':
            print(f"Updated: {xx}\tFrom: {auth_jira.issue(f'{xx}').fields.priority}\tTo: {yy}")
        elif sys.argv[1] == 'prod':
            set_new_priority(auth_jira, x, new_priority)
        else:
            print('No setting set am I: test or prod')
            sys.exit()

if __name__ == '__main__':
    main()
