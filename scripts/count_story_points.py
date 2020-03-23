#!/usr/bin/env python3

import getpass
import requests
import functools

READY_FOR_REVIEW_COLUMN = "Ready for Sprint Review"

WEEKLY_SPRINT_PROJECT = "Weekly Sprint"
IN_PROGRESS = "In Progress"
CURRENT_SPRINT = "Current Sprint"
BUGS = "Bugs"
HEADERS = {
    "Accept": "application/vnd.github.v3+json application/vnd.github.inertia-preview+json application/vnd.github.symmetria-preview+json"}


def get_organisation_projects():
    url = "https://api.github.com/orgs/deNBI/projects"
    headers = HEADERS
    r = requests.get(
        url=url,
        headers=headers,
        auth=(USER_NAME, PASSWORD),

    )
    return r.json()


def get_issue(content_url):
    url = content_url
    r = requests.get(
        url=url,
        headers=HEADERS,
        auth=(USER_NAME, PASSWORD),

    )
    return r.json()


def filter_projects(filter_name, projects):
    for project in projects:
        if filter_name == project['name']:
            return project
    return None


def get_project_columns(project):
    url = "https://api.github.com/projects/{}/columns".format(project["id"])
    headers = HEADERS
    r = requests.get(
        url=url,
        headers=headers,
        auth=(USER_NAME, PASSWORD),

    )
    return r.json()


def get_specific_column(filter_name, columns):
    for column in columns:
        if filter_name == column['name']:
            return column
    return None


def get_cards_by_columns(column):
    url = "https://api.github.com/projects/columns/{}/cards".format(column["id"])
    r = requests.get(
        url=url,
        headers=HEADERS,
        auth=(USER_NAME, PASSWORD),

    )
    cards = r.json()
    while "next" in r.links:
        print("Next Page: {}".format(r.links["next"]["url"]))
        r = requests.get(
            url=r.links["next"]["url"],
            headers=headers,
            auth=(USER_NAME, PASSWORD),

        )
        cards.extend(r.json())

    return cards


def count_reevaluation_cards(cards):
    counter = 0
    for card in cards:
        card_counter = []
        labels = get_issue(card['content_url'])['labels']
        for label in labels:
            label_value = label['name']
            if label_value.isdigit():
                card_counter.append(int(label_value))
        if len(card_counter) > 1:
            counter_diff = functools.reduce(lambda a, b: abs(a - b), card_counter)
            counter += counter_diff
    return counter


def count_min_points_with_post_bugs(cards):
    counter_done = 0
    counter_bugs = 0
    for card in cards:
        values = []
        try:
            labels = get_issue(card['content_url'])['labels']
            if not "post-meeting" in [l['name'] for l in labels]:
                for label in labels:
                    label_value = label['name']
                    if label_value.isdigit():
                        values.append(int(label_value))
                counter_done += min(values)
            else:
                for label in labels:
                    label_value = label['name']
                    if label_value.isdigit():
                        values.append(int(label_value))
                counter_bugs += min(values)
        except:
            pass

    return counter_done, counter_bugs


def count_min_points(cards):
    counter = 0
    for card in cards:
        values = []
        try:
            labels = get_issue(card['content_url'])['labels']
            if not "post-meeting" in [l['name'] for l in labels]:
                for label in labels:
                    label_value = label['name']
                    if label_value.isdigit():
                        values.append(int(label_value))
                counter += min(values)
        except:
            pass

    return counter


def count_done_points(columns):
    column = get_specific_column(filter_name=READY_FOR_REVIEW_COLUMN, columns=columns)
    cards = get_cards_by_columns(column=column)
    done, bugs = count_min_points_with_post_bugs(cards)
    print("Done: {}\nBugs: {}".format(done, bugs))


def count_done_reevalation(columns):
    column = get_specific_column(filter_name=IN_PROGRESS, columns=columns)
    cards = get_cards_by_columns(column=column)
    print("Gone to Re-evaluation: {}".format(count_reevaluation_cards(cards)))


def count_planned_points(columns):
    column = get_specific_column(filter_name=CURRENT_SPRINT, columns=columns)
    cards = get_cards_by_columns(column=column)
    current_points = count_min_points(cards)
    column = get_specific_column(filter_name=BUGS, columns=columns)
    cards = get_cards_by_columns(column=column)
    bugs_points = count_min_points(cards)
    column = get_specific_column(filter_name=IN_PROGRESS, columns=columns)

    cards = get_cards_by_columns(column=column)
    in_progress_planned = count_min_points(cards)
    full = int(current_points) + int(bugs_points) + int(in_progress_planned)
    print("Planned points: {}".format(full))


if __name__ == "__main__":
    print("Enter username:")
    USER_NAME = input()
    print("Enter password:")
    PASSWORD = getpass.getpass()
    projects = get_organisation_projects()
    weekly_project = filter_projects(filter_name=WEEKLY_SPRINT_PROJECT, projects=projects)
    columns = get_project_columns(weekly_project)
    count_done_points(columns)
    count_done_reevalation(columns)
    count_planned_points(columns)