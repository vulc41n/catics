from rest_framework.exceptions import APIException

class NoUnitsLeftException(APIException):
    status_code = 400
    default_code = 'no_units_left'

    def __init__(self, is_cat):
        self.default_detail = 'Il ne vous reste plus de {}'.format('chat' if is_cat else 'chatton')
        super().__init__()

class OccupiedException(APIException):
    status_code = 400
    default_code = 'occupied'
    default_detail = 'Cette case est déjà occupée'

class PromotionException(APIException):
    status_code = 400
    default_code = 'promotion'
    default_detail = 'Une promotion est en attente'
