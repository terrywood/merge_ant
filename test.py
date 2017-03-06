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

user = easytrader.use('gf', debug=False)
user.prepare('gf.json')
gf_positions = user.get_position()
logger.info("trading...........")
logger.info(gf_positions)