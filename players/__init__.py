from .basic_queue_player import BasicQueuePlayer
from .advanced_queue_player import AdvancedQueuePlayer
from .first_card_player import FirstCardPlayer
from .advanced_sort_variants import Sort1Player, Sort2Player, Sort3Player
from .protecting_player import (
    BorderlineHintPlayer,
    ProtectingPlayer,
    ProtectSort1Player,
    ProtectSort2Player,
    ProtectSort3Player,
    ProtectSort4Player,
)
from .info_player import InfoPlayer

STRATEGIES = {
    "FIRST_CARD": FirstCardPlayer,
    "BASIC_QUEUE": BasicQueuePlayer,
    "ADVANCED_QUEUE": AdvancedQueuePlayer,
    "SORT_1": Sort1Player,
    "SORT_2": Sort2Player,
    "SORT_3": Sort3Player,
    "PROTECT": ProtectingPlayer,
    "PROTECT_SORT_1": ProtectSort1Player,
    "PROTECT_SORT_2": ProtectSort2Player,
    "PROTECT_SORT_3": ProtectSort3Player,
    "PROTECT_SORT_4": ProtectSort4Player,
    "BORDERLINE": BorderlineHintPlayer,
    "INFO": InfoPlayer,
}
