from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        yield Demographics, dict(age=24, gender='Male')

        yield (
            CognitiveReflectionTest,
            dict(crt_bat=10, crt_widget=5, crt_lake=48),
        )

        for value in [self.player.crt_bat, self.player.payoff]:
            expect(value, '!=', None)
