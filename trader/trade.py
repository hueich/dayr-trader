#!/usr/bin/env python

from __future__ import division
import argparse
import collections
import csv
import pprint

TRADE_DATA_FILE = 'trade-data.csv'

Trade = collections.namedtuple('Trade', ['location', 'from_count', 'from_item', 'to_count', 'to_item'])

class Transaction(object):
	def __init__(self, direction, count, trade):
		self.direction = direction
		self.count = count
		self.trade = trade

	def __str__(self):
		if self.direction == 'from':
			from_count = self.count
			to_count = self.trade.to_count * self.count / self.trade.from_count
		else:
			from_count = self.trade.from_count * self.count / self.trade.to_count
			to_count = self.count
		parts = ['From', '%g' % from_count, self.trade.from_item, 'to', '%g' % to_count, self.trade.to_item, 'at', self.trade.location]
		return ' '.join(parts)

	def __repr__(self):
		return str(self)


def find_trade_routes_from(from_count, from_item, from_map, used_trades=None, starting_item=None):
	used_trades = used_trades or set()
	starting_item = starting_item or from_item
	new_routes = []
	for trade in [t for t in from_map.get(from_item, []) if t not in used_trades and not (used_trades and t.from_item == starting_item)]:
		to_count = trade.to_count * from_count / trade.from_count
		transaction = Transaction('to', to_count, trade)
		used_trades.add(trade)
		sub_routes = find_trade_routes_from(to_count, trade.to_item, from_map, used_trades, starting_item)
		used_trades.remove(trade)
		new_routes.append([transaction] + sub_routes)
	if len(new_routes) == 1:
		new_routes = new_routes[0]
	return new_routes


def find_trade_routes_to(to_count, to_item, to_map, used_trades=None, starting_item=None):
	used_trades = used_trades or set()
	starting_item = starting_item or to_item
	new_routes = []
	for trade in [t for t in to_map.get(to_item, []) if t not in used_trades and not (used_trades and t.to_item == starting_item)]:
		from_count = trade.from_count * to_count / trade.to_count
		transaction = Transaction('from', from_count, trade)
		used_trades.add(trade)
		sub_routes = find_trade_routes_to(from_count, trade.from_item, to_map, used_trades, starting_item)
		used_trades.remove(trade)
		new_routes.append([transaction] + sub_routes)
	if len(new_routes) == 1:
		new_routes = new_routes[0]
	return new_routes


def main():
	parser = argparse.ArgumentParser(description='Print trade routes for Day R traders.')
	parser.add_argument('trade_direction', metavar='DIRECTION', choices=('to', 'from'),
						help='Direction of trade')
	parser.add_argument('count', metavar='COUNT', type=int,
						help='Amount to trade')
	parser.add_argument('item', metavar='ITEM',
						help='Item to trade')
	parser.add_argument('--trade_data_file', default=TRADE_DATA_FILE,
						help='CSV file with trade data')
	args = parser.parse_args()

	items = set()
	from_map = {}
	to_map = {}
	trades = set()
	with open(args.trade_data_file) as f:
		reader = csv.DictReader(f)
		for row in reader:
			items.add(row['FromItem'])
			items.add(row['ToItem'])
			trade = Trade(
				location=row['Location'],
				from_count=int(row['FromCount']),
				from_item=row['FromItem'],
				to_count=int(row['ToCount']),
				to_item=row['ToItem'],
			)
			trades.add(trade)
			from_map.setdefault(trade.from_item, set()).add(trade)
			to_map.setdefault(trade.to_item, set()).add(trade)

	if args.item not in items:
		print 'Item', args.item, 'is not tradable. Tradable ones are:\n ', '\n  '.join(sorted(items))
		return 1

	if args.trade_direction == 'to':
		print 'Trading to', args.count, args.item
		routes = find_trade_routes_to(args.count, args.item, to_map)
	else:
		print 'Trading from', args.count, args.item
		routes = find_trade_routes_from(args.count, args.item, from_map)

	pp = pprint.PrettyPrinter(indent=2, width=1)
	pp.pprint(routes)


if __name__ == '__main__':
	main()
