# -*- coding: utf-8 -*-
import email
import email.header
import imaplib
import json
import time
import util
import easytrader
from datetime import datetime
from easytrader import helpers
from log import logger

config = {}
positions = {}
user = {}


def parse(content):
    index1 = content.find("Hold1") - 2
    index2 = content.find("Total_profit_rate") - 2
    if index1 > 0:
        working = json.loads(content[0:index1])
        position = json.loads(content[index1:index2])
        buy_list = []
        for code in working['buy']:
            for tick in position:
                if position[tick]['code'] == code:
                    entity = position[tick]
                    buy_list.append(entity)
                    break

        working['buy'] = buy_list
        return working
    else:
        logger.info(index1)
        if index1 == -3:
            return json.loads(content[0:index2 - 2])
            logger.info(content[0:index2 - 2])
        else:
            return json.loads(content[0:index2])
            logger.info(content[0:index2])


def mail():
    logger.info("handle mail function...........")
    content_info = None
    conn = imaplib.IMAP4(config['mail_host'])
    conn.login(config['mail_user'], config['mail_pass'])
    conn.select()
    typ, mail_data = conn.search(None, 'ALL')
    if typ != 'OK':
        logger.warn("No messages found!")
        return
    # typ, data = conn.search(None, '(FROM "ants2016")')
    for num in mail_data[0].split():
        # typ, data = conn.fetch(num, '(RFC822)')
        typ, mail_data = conn.fetch(num, '(RFC822)')
        if typ != 'OK':
            logger.warn("ERROR getting message", num)
            return
        msg = email.message_from_bytes(mail_data[0][1])
        message_id = msg.get('Message-ID')

        logger.info(message_id)
        fr = email.utils.parseaddr(msg['From'])[1]
        if fr != 'ants2016@vip.163.com':
            continue

        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            if not util.is_today(local_date):
                continue
        else:
            logger.warn('can not get date tuple')
            continue
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        for name in config['group']:
            if subject.startswith(name):
                logger.info(subject)
                with open(name + '.txt', 'r') as f1:
                    old_id = (f1.read()).format()
                    if old_id == message_id.format():
                        logger.info('mail is handled')
                        content_info = '{"date": "", "sell": [], "buy": []}{"Total_profit_rate": "0%"}'
                        logger.info(content_info)
                    else:
                        logger.info('mail is handled 3' + message_id)
                        with open(name + '.txt', 'w') as f2:
                            f2.write(message_id)
                            for part in msg.walk():
                                content_info = part.get_payload(decode=True).decode()
                                content_info = content_info[0:content_info.find("\n")]
                                logger.info(content_info)
                                trading(content_info)

    conn.close()
    conn.logout()
    if datetime.now().minute > 35:
        return
    elif content_info is None:
        time.sleep(30)
        mail()


def read_config(path):
    try:
        global config
        config = helpers.file2dict(path)
    except ValueError:
        logger.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text')


def balk() -> object:
    while True:
        if util.is_trade_date():
            if datetime.now().hour > 9:
                break
            elif datetime.now().minute > 26 and datetime.now().hour == 9:
                logger.info('is trade day ready')
                break
            else:
                time.sleep(20)
        else:
            logger.info('sleep 663 sec')
            time.sleep(663)


def main():
    balk()
    read_config("ant.json")
    logger.info(config)
    global user
    logger.info("login gf")
    user = easytrader.use('gf', debug=True)
    logger.info("login gf2")
    user.prepare('gf.json')
    logger.info("login gf3")
    mail()


def trading(data):
    data = parse(data)
    gf_positions = user.get_position()
    logger.info("trading...........")
    logger.info(gf_positions)
    logger.info(data)

    for sell_code in data['sell']:
        sell_code = sell_code[0:6].format()
        message = 'sell clear  code ' + sell_code
        logger.info(message)
        for position in gf_positions['data']:
            stock_code = position['stock_code']
            if stock_code == sell_code:
                amount = position['enable_amount']
                last_price = position['last_price']
                result = user.sell(sell_code, price=last_price, amount=amount)
                logger.info(result)
                message = 'sell clear code = ' + sell_code + ' amount=' + amount + ' last price=' + last_price
                logger.info(message)
                break

    for buy_entity in data['buy']:
        buy_code = buy_entity['code']
        buy_code = buy_code[0:6].format()
        volume = buy_entity['Weight'] * config['balance'] / 100
        cost = buy_entity['Cost']
        result = user.buy(buy_code, price=cost, volume=volume)
        logger.info(result)
        message = 'buy  code=' + buy_code + ' balance=' + str(volume) + ' last price=' + str(cost)
        logger.info(message)
    logger.info("ant working ending")


if __name__ == '__main__':
    main()
