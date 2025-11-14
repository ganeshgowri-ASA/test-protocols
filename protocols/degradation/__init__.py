"""
Degradation Testing Protocols

15 protocols for various degradation mechanisms
"""

from .lid_001 import LID001Protocol
from .letid_001 import LETID001Protocol
from .pid_001 import PID001Protocol
from .pid_002 import PID002Protocol
from .uvid_001 import UVID001Protocol
from .sponge_001 import SPONGE001Protocol
from .snail_001 import SNAIL001Protocol
from .delam_001 import DELAM001Protocol
from .corr_001 import CORR001Protocol
from .chalk_001 import CHALK001Protocol
from .yellow_001 import YELLOW001Protocol
from .crack_001 import CRACK001Protocol
from .solder_001 import SOLDER001Protocol
from .jbox_001 import JBOX001Protocol
from .seal_001 import SEAL001Protocol

__all__ = [
    'LID001Protocol', 'LETID001Protocol', 'PID001Protocol', 'PID002Protocol',
    'UVID001Protocol', 'SPONGE001Protocol', 'SNAIL001Protocol', 'DELAM001Protocol',
    'CORR001Protocol', 'CHALK001Protocol', 'YELLOW001Protocol', 'CRACK001Protocol',
    'SOLDER001Protocol', 'JBOX001Protocol', 'SEAL001Protocol'
]
