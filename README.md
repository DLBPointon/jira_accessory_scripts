# jira_accessory_scripts
This rep will contain a number of scripts developed to interact with a Jira instance.

## Priority Check
This script scans the decon status for tickets,
downloads the ticket.yaml and parses for a priority flag.

If this flag does not exist then it is assigned "low",
if the ticket belongs to a certain project then it will be assigned "highest"
else it will check the yaml.

Newly assigned priorities will then be set on the relevant jira ticket.
