from .basic_queue_player import BasicQueuePlayer
from .first_card_player import FirstCardPlayer

STRATEGIES = {
    "FIRST_CARD": FirstCardPlayer,
    "BASIC_QUEUE": BasicQueuePlayer,
}
