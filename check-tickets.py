import csv
import operator
import itertools

import click
from unidecode import unidecode


class CSV(click.File):
    name = 'csv'

    def convert(self, value, param, ctx):
        f = super(CSV, self).convert(value, param, ctx)
        return csv.DictReader(f)


@click.command()
@click.argument('tickets', type=CSV())
@click.argument('waitlists', type=CSV())
def check_tickets(tickets, waitlists):
    tickets = (
        [parse_row_from_tickets(row) for row in tickets] +
        [parse_row_from_waitlists(row) for row in waitlists]
    )
    email_name_pairs = [(t['email'], t['name']) for t in tickets]

    email_name_pairs.sort(key=operator.itemgetter(0))
    pairs_by_email = itertools.groupby(email_name_pairs, operator.itemgetter(0))
    for email, group in pairs_by_email:
        names = set(pair[1] for pair in group)
        if len(names) != 1:
            error(f"email '{email}' has multiple names: " + ', '.join(names))

    email_name_pairs.sort(key=operator.itemgetter(1))
    pairs_by_name = itertools.groupby(email_name_pairs, operator.itemgetter(1))
    for name, group in pairs_by_name:
        emails = set(pair[0] for pair in group)
        if len(emails) != 1:
            error(f"name '{name}' has multiple emails: " + ', '.join(emails))

    tickets.sort(key=operator.itemgetter('email'))
    tickets_by_email = itertools.groupby(tickets, operator.itemgetter('email'))
    for email, group in tickets_by_email:
        group = list(group)

        conference = [t['ticket'] for t in group if not t['is_workshop']]
        if len(conference) < 1:
            error(f"'{email}' has no conference ticket")
        elif len(conference) > 1:
            error(f"'{email}' has multiple conference tickets: "
                  + ', '.join(conference))

        workshops_by_time = {}
        overlapping_workshops = set()
        for ticket in group:
            if ticket['is_workshop'] and not ticket['is_waitlist']:
                if ticket['time'] in workshops_by_time:
                    overlapping_workshops.add(workshops_by_time[ticket['time']])
                    overlapping_workshops.add(ticket['ticket'])
                else:
                    workshops_by_time[ticket['time']] = ticket['ticket']
        if overlapping_workshops:
            error(f"'{email}' has overlapping workshop tickets:\n » "
                  + '\n » '.join(overlapping_workshops))

        registered_workshops = dict([
            (t['time'], t['ticket']) for t in group
            if t['is_workshop'] and not t['is_waitlist']
        ])
        invalid_waitlists = {}
        for ticket in group:
            if ticket['is_workshop'] and ticket['is_waitlist']:
                if ticket['time'] in registered_workshops:
                    invalid_waitlists[ticket['time']] = ticket['ticket']
        if invalid_waitlists:
            overlapping_workshops = [
                ticket for (time, ticket) in registered_workshops.items()
                if time in invalid_waitlists
            ]
            error(f"'{email}' is in waitlists for times when already attending a workshop:"
                  + '\n » WAITLIST '
                  + '\n » WAITLIST '.join(invalid_waitlists.values())
                  + '\n » WORKSHOP '
                  + '\n » WORKSHOP '.join(overlapping_workshops))


def parse_row_from_tickets(row):
    is_workshop, time = parse_ticket(row['Ticket'])
    return {
        'ticket': row['Ticket'],
        'name': unidecode(row['Ticket Full Name'].lower()),
        'email': row['Ticket Email'].lower(),
        'time': time,
        'is_waitlist': False,
        'is_workshop': is_workshop,
    }


def parse_row_from_waitlists(row):
    is_workshop, time = parse_ticket(row['Ticket'])
    return {
        'ticket': row['Ticket'],
        'name': unidecode(row['Name'].lower()),
        'email': row['Email'].lower(),
        'time': time,
        'is_waitlist': True,
        'is_workshop': is_workshop,
    }


def parse_ticket(ticket):
    if ' – ' in ticket:
        return True, ticket.split(' – ', 1)[0]
    return False, None


def error(message):
    prefix = click.style('[ERROR] ', fg='red', bold=True)
    click.echo(prefix + message, err=True)


if __name__ == '__main__':
    check_tickets()
