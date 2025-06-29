from rest_framework.exceptions import APIException

class ExpiredException(APIException):
    status_code = 410
    default_code = 'expired'
    default_detail = 'Votre code d\'activation a expiré'
