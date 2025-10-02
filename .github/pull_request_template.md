## Description

Describe what this pull request changes, and why. Include implications for people using this change.

## Supporting information

Link to other information about the change, such as Jira issues, GitHub issues, or Discourse discussions.
Be sure to check they are publicly readable, or if not, repeat the information here.

## Testing instructions

Please provide detailed step-by-step instructions for testing this change.

## Deadline

"None" if there's no rush, or provide a specific date or event (and reason) if there is one.

## Other information

Include anything else that will help reviewers and consumers understand the change.

- Does this change depend on other changes elsewhere?
- Any special concerns or limitations? For example: deprecations, migrations, security, or accessibility.
- If your [database migration](https://openedx.atlassian.net/wiki/spaces/AC/pages/23003228/Everything+About+Database+Migrations) can't be rolled back easily.

## Pre-merge checklist:

- [ ] `make format` has been run
- [ ] This has been manually installed in a Tutor devstack and:
  - [ ] manual testing steps have been followed (as described in ./docs/manual-test-plan.md)
  - [ ] `make test_migrations` has been run
