def sort_by_price(tickets, order):
    if 'ascending' in order:
        return tickets.order_by('price')
    else:
        return tickets.order_by('-price')


def sort_by_datetime(tickets, order):
    if 'ascending' in order:
        return tickets.order_by('date', 'time')
    else:
        return tickets.order_by('-date', '-time')


def sort_by_amount(tickets, order):
    if 'ascending' in order:
        return tickets.order_by('amount')
    else:
        return tickets.order_by('-amount')
