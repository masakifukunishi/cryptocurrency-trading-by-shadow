import configparser

conf = configparser.ConfigParser()
conf.read('settings/settings.ini')

gmo_api_key = conf['gmo']['api_key']
gmo_api_secret = conf['gmo']['api_secret']
gmo_public_end_point = conf['gmo']['public_end_point']
gmo_private_end_point = conf['gmo']['private_end_point']
gmo_send_order_path = conf['gmo']['send_order_path']
gmo_send_bulk_close_order_path = conf['gmo']['send_bulk_close_order_path']
gmo_send_cancel_bulk_order_path = conf['gmo']['send_cancel_bulk_order_path']
gmo_send_cancel_order_path = conf['gmo']['send_cancel_order_path']
gmo_send_cancel_orders_path = conf['gmo']['send_cancel_orders_path']
gmo_get_orderbooks_path = conf['gmo']['get_orderbooks_path']
gmo_get_order_path = conf['gmo']['get_order_path']

product_code = conf['currency']['product_code']

use_coin = float(conf['trading']['use_coin'])
target_size = float(conf['trading']['target_size'])