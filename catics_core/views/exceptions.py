from rest_framework.exceptions import APIException

class NotYourTurnException(APIException):
    status_code = 400
    default_code = 'not_your_turn'
    default_detail = 'Ce n\'est pas à votre tour de jouer'

class InvalidUnitsException(APIException):
    status_code = 400
    default_code = 'invalid_units'
    default_detail = 'Ces unités ne peuvent pas être promues'

class NotAPlayerException(APIException):
    status_code = 403
    default_code = 'not_a_player'
    default_detail = 'Vous n\'êtes pas un joueur de cette partie'
