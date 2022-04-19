'''
Enum Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
import enum

class Status(enum.Enum):
  FAILED = 0
  SUCCESS = 1

  def __repr__(self) -> str:
    return self.name.lower()
