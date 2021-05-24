from py3cw.request import Py3CW

API_key = ''
SECRET_key = ''
account = ''        # Copy the number from the URL when you go to the page for the exchange on 3commas. eg. https://3commas.io/accounts/12345678 you enter '12345678'
btc_bot_name = ''   # Enter the exact name of your BTC SDCA bot as it is named on 3Commas (case sensitive)
btc_capital =       # Enter the amount of BTC you are allocating to the above BTC bot
usdt_bot_name = ''  # Enter the exact name of your USDT SDCA bot as it is named on 3Commas (case sensitive)
usdt_capital =      # Enter the amount of USDT you are allocating to the above USDT bot
reserve = 0.25      # Proportion of capital you want to keep in reserve for 7th safety order and above 0.25 = 25% (as recommended in the strategy guide)


### Please do not change anything below this line unless you know what you are doing.
allocations = {
    'btc_bot_name': btc_bot_name,
    'btc_capital': btc_capital, 
    'btc_bot_price': 0.006195, # The price of one bot (usually to 6 SOs)
    'usdt_bot_name': usdt_bot_name,
    'usdt_capital': usdt_capital, 
    'usdt_bot_price': 227.81, # # The price of one bot (usually to 6 SOs)
    'reserve': reserve, 
}

p3cw = Py3CW(
    key=API_key, 
    secret=SECRET_key,
    request_options={
        'request_timeout': 50,
        'nr_of_retries': 1,
        'retry_status_codes': [502]
    }
)


# Get enabled bots info
error, bots = p3cw.request(
    entity='bots',
    action='',
    payload={
        "limit": 50,
        "scope": 'enabled',
        "account_id": account,
    }
) 

# Get bot id for usdt and btc
btc_bot_id = 0
usdt_bot_id = 0


#Get active deals info
error, deals = p3cw.request(
    entity='deals',
    action='',
    payload={
        "limit": 1000,
        "scope": 'active',
        "account_id": account,
    }
)

def calc_max_deals(percentage, capital, price):
    max_cap = (capital * (1 - allocations['reserve'])) * percentage
    max_deals = int(max_cap/price)

    return max_deals

def calc_percentage(SO_per_deal):
    # When SO per deal <= 1 --> 200% usage
    # When SO per deal <= 2 --> 175%
    # When SO per deal <= 3 --> 150%
    # When SO per deal <= 4 --> 125%
    # When SO per deal > 4 --> 100%
    if SO_per_deal <= 1:
        return 2.0
    elif SO_per_deal <= 2:
        return 1.75
    elif SO_per_deal <= 3:
        return 1.5
    elif SO_per_deal <= 5:
        return 1.25
    else:
        return 1.0

def update_max_deals(bot_id, max_deals, name, pairs, bo, tp, so, mvc, msc, mso, asoc, sosp, tpt, sl):
    error, data = p3cw.request(
        entity='bots', 
        action='update',
        action_id=str(bot_id),
        payload={
            "name": name,
            "pairs": pairs,
            "max_active_deals": int(max_deals),
            "base_order_volume": float(bo),
            "take_profit": float(tp),
            "safety_order_volume": float(so),
            "martingale_volume_coefficient": float(mvc),
            "martingale_step_coefficient": float(msc),
            "max_safety_orders": int(mso),
            "active_safety_orders_count": int(asoc),
            "safety_order_step_percentage": float(sosp),
            "take_profit_type": tpt,
            "strategy_list": sl,
            "bot_id": int(bot_id)
        }
    )

usdt_comp_so_count = 0
usdt_active_deals_count = 0
btc_comp_so_count = 0
btc_active_deals_count = 0


for deal in deals:
    if deal['bot_name'] == allocations['btc_bot_name']:
        btc_comp_so_count += deal['completed_safety_orders_count']
        btc_active_deals_count += 1
    elif deal['bot_name'] == allocations['usdt_bot_name']:
        usdt_comp_so_count += deal['completed_safety_orders_count']
        usdt_active_deals_count += 1

usdt_so_per_deal = usdt_comp_so_count / usdt_active_deals_count
btc_so_per_deal = btc_comp_so_count / btc_active_deals_count

btc_percentage = calc_percentage(btc_so_per_deal)
usdt_percentage = calc_percentage(usdt_so_per_deal)

btc_max_deals = calc_max_deals(btc_percentage, allocations['btc_capital'], allocations['btc_bot_price'])
usdt_max_deals = calc_max_deals(usdt_percentage, allocations['usdt_capital'], allocations['usdt_bot_price'])

for bot in bots:
    if bot['name'] == allocations['btc_bot_name']:
        btc_bot_id = bot['id']

        if bot['max_active_deals'] != btc_max_deals:
            update_max_deals(
                btc_bot_id, 
                btc_max_deals, 
                bot['name'],
                bot['pairs'], 
                bot['base_order_volume'],
                bot['take_profit'],
                bot['safety_order_volume'],
                bot['martingale_volume_coefficient'],
                bot['martingale_step_coefficient'],
                bot['max_safety_orders'], 
                bot['active_safety_orders_count'], 
                bot['safety_order_step_percentage'],
                bot['take_profit_type'],
                bot['strategy_list']
                )
            print(bot['name'] + ' max active deals updated to ' + str(btc_max_deals))
        else:
            print('Max deals unchanged.')
    elif bot['name'] == allocations['usdt_bot_name']:
        usdt_bot_id = bot['id']
        if bot['max_active_deals'] != usdt_max_deals:
            # bot_id, max_deals, name, pairs, bo, tp, so, mvc, msc, mso, asoc, sosp, tpt, sl
            update_max_deals(
                bot_id=usdt_bot_id, 
                max_deals=usdt_max_deals, 
                name=bot['name'],
                pairs=bot['pairs'], 
                bo=bot['base_order_volume'],
                tp=bot['take_profit'],
                so=bot['safety_order_volume'],
                mvc=bot['martingale_volume_coefficient'],
                msc=bot['martingale_step_coefficient'],
                mso=bot['max_safety_orders'], 
                asoc=bot['active_safety_orders_count'], 
                sosp=bot['safety_order_step_percentage'],
                tpt=bot['take_profit_type'],
                sl=bot['strategy_list']
                )
            print(bot['name'] + ' max active deals updated to ' + str(usdt_max_deals))
        else:
            print('Max deals unchanged.')

print('BTC bot ID: ' + str(btc_bot_id))
print('BTC: ' + str(btc_max_deals))
print('USDT bot ID: ' + str(usdt_bot_id))
print('USDT: ' + str(usdt_max_deals))
