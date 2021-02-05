#!/usr/bin/env python

# This file is part of krakenex.
# Licensed under the Simplified BSD license. See `examples/LICENSE.txt`.

# FIXME: Prints the sum of _some_ open positions?..

# Maintainer: Austin.Deric@gmail.com (@AustinDeric on github)
LAST_ORDERS = 5

#fix pair names
FIX_X_PAIR_NAMES = ['XETHEUR', 'XLTCEUR']

# Exclude
EXCLUDE_PAIR_NAMES = ['ZEUREUR', 'BSVEUR']

PAIR_TO_LAST_ORDER = ['SCEUR']

# configure api
import krakenex

k = krakenex.API()
k.load_key('kraken.key')

# prepare request
# req_data = {'docalcs': 'true'}
req_data = {'trades': 'false'}

# query servers
start = k.query_public('Time')

balance = k.query_private('Balance')
# trade_balance = k.query_private('TradeBalance')
open_orders = k.query_private('OpenOrders', req_data)
closed_orders = k.query_private('ClosedOrders', req_data)
trades_history = k.query_private('TradesHistory', req_data)

end = k.query_public('Time')
latency = end['result']['unixtime'] - start['result']['unixtime']
currency = 'EUR'
pair_names_dict = {}
sells_amount = 0
buys_amount = 0


def entries_to_remove(entries, the_dict):
    for key in entries:
        if key in the_dict:
            del the_dict[key]


def get_amount_from_order(order_string):
    words = order_string.split()
    price = words[1]
    shares = words[-1]
    return float(price) * float(shares)


def get_fix_pair_name(pair_name):
    if pair_name[:2] == 'XX' or pair_name in FIX_X_PAIR_NAMES:
        return pair_name[1:]
    return pair_name


# Read pair names
for key, value in balance['result'].items():
    key_name = key[1:]+currency if key[0] == key[1] == 'X' else key+currency
    pair_names_dict[key_name] = {'name': key_name,
                                 'orders': [],
                                 'trades': [],
                                 'buy_amount': 0.0,
                                 'sell_amount': 0.0,
                                 }

entries_to_remove(EXCLUDE_PAIR_NAMES, pair_names_dict)

for fix_pair_name in FIX_X_PAIR_NAMES:
    pair_names_dict[fix_pair_name[1:]] = pair_names_dict[fix_pair_name]
    del pair_names_dict[fix_pair_name]


# Print names on balance
print(pair_names_dict.keys())

print('\n OPEN ORDERS READ:')
for _, order in open_orders['result']['open'].items():
    order_detail = order['descr']
    pair_name = order_detail['pair']
    pair = pair_names_dict.get(pair_name)

    if pair:
        pair['orders'].append(order_detail['order'])
        amount = get_amount_from_order(order_detail['order'])
        if order_detail['type'] == 'buy':
            pair['buy_amount'] += amount
            buys_amount += amount
        else:
            pair['sell_amount'] += amount
            sells_amount += amount
    else:
        print('Missing order pair: {}'.format(pair_name))

print('\n TRADES:')
for _, order in closed_orders['result']['closed'].items():
    order_detail = order['descr']
    pair_name = order_detail['pair']
    pair = pair_names_dict.get(pair_name)

    if pair:
        pair['trades'].append(order_detail['order'])
    else:
        print('Missing order pair: {}'.format(pair_name))

# for _, trade in trades_history['result']['trades'].items():
#     pair_name = get_fix_pair_name(trade['pair'])
#     pair = pair_names_dict.get(pair_name)
#
#     if pair:
#         pair['trades'].append('{} {} @ {}'.format(trade['type'], trade['vol'], trade['price']))
#     else:
#         print('Missing trade pair: {}'.format(pair_name))

print('\n ORDERS TO CREATE:')
for _, pair in pair_names_dict.items():
    if not pair['buy_amount']:
        print('Missing buy for pair: {}'.format(pair['name']))

    if not pair['sell_amount']:
        print('Missing sell for pair: {}'.format(pair['name']))

#Last trades
for pair_name in PAIR_TO_LAST_ORDER:
    pair = pair_names_dict.get(pair_name)
    print('\n**** Open orders for asset: {}.'.format(pair_name))
    for order in pair['orders'][:LAST_ORDERS]:
        print('\n {}'.format(order))

    print('\n**** Trades for asset: {}.'.format(pair_name))
    for trade in pair['trades'][:LAST_ORDERS]:
        print('\n {}'.format(trade))

print('\n ***** SUMMARY ***** ')
print(' Total Sell amount: {}. \n Total Buys amount: {}.'.format(sells_amount,buys_amount))

print('latency: {} sec'.format(latency))


