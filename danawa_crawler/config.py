from enum import Enum
from enum import IntEnum


class LOGLEVEL(IntEnum):
    D = 0
    I = 1
    E = 2


CFG_APP_VERSION_CODE = 1

CFG_LOGLEVEL = LOGLEVEL.D
