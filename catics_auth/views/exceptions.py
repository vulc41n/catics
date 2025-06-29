from rest_framework.exceptions import APIException

class ExpiredException(APIException):
    status_code = 410
    default_code = 'expired'
    default_detail = 'Votre code d\'activation a expiré'

class ChallengeForAnotherEmailException(APIException):
    status_code = 400
    default_code = 'challenge_for_another_email'
    default_detail = 'Ce challenge a été généré pour une autre adresse email'

class ChallengeFailException(APIException):
    status_code = 400
    default_code = 'challenge_fail'
    default_detail = 'Le challenge n\'a pas été rempli'
