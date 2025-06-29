from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    player1_type = models.ForeignKey(
        ContentType,
        limit_choices_to={ 'model__in': ['user', 'agentversion'] },
        on_delete=models.SET_NULL,
        related_name='games_as_player1',
        null=True,
    )
    player1_id = models.PositiveBigIntegerField()
    player1_object = GenericForeignKey('player1_type', 'player1_id')

    player2_type = models.ForeignKey(
        ContentType,
        limit_choices_to={ 'model__in': ['user', 'agentversion'] },
        on_delete=models.SET_NULL,
        related_name='games_as_player2',
        null=True,
    )
    player2_id = models.PositiveBigIntegerField()
    player2_object = GenericForeignKey('player2_type', 'player2_id')

    is_p1_turn = models.BooleanField(default=True)

    n_kittens_p1 = models.PositiveIntegerField(default=8)
    n_cats_p1 = models.PositiveIntegerField(default=0)

    n_kittens_p2 = models.PositiveIntegerField(default=8)
    n_cats_p2 = models.PositiveIntegerField(default=0)

    board = models.JSONField(default=dict)

    promotions = models.JSONField(default=list)

    winner = models.CharField(
        choices=(('n', 'nobody'), ('1', 'player 1'), ('2', 'player 2')),
        max_length=1,
        default='n',
    )

    def clean(self):
        if self.player1_type.model not in ['User', 'AgentVersion']:
            raise ValidationError({
                'player1_type': 'Le joueur 1 doit être un utilisateur ou un agent. Type: ' \
                    + self.player1_type.model
            })
        if self.player2_type.model not in ['User', 'AgentVersion']:
            raise ValidationError({
                'player2_type': 'Le joueur 2 doit être un utilisateur ou un agent. Type: ' \
                    + self.player2_type.model
            })
