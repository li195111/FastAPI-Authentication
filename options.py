'''
Options Module
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from argparse import Namespace

OPTIONS = None


def get_opts():
  global OPTIONS
  if OPTIONS is None:
    OPTIONS = Namespace()
  return OPTIONS


def update_opts(opts):
  global OPTIONS
  OPTIONS = opts
  return OPTIONS
