from .basic_queue_player import BasicQueuePlayer
from .advanced_queue_player import AdvancedQueuePlayer
from .first_card_player import FirstCardPlayer
from .advanced_sort_variants import Sort1Player, Sort2Player, Sort3Player

STRATEGIES = {
    "FIRST_CARD": FirstCardPlayer,
    "BASIC_QUEUE": BasicQueuePlayer,
    "ADVANCED_QUEUE": AdvancedQueuePlayer,
    "SORT_1": Sort1Player,
    "SORT_2": Sort2Player,
    "SORT_3": Sort3Player,
}
