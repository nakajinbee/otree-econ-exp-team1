from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    Gender = models.CharField(
        label='あなたの名前：')
    CRT1 = models.CharField(
        choices=('あなた100相手200','あなた100相手100','あなた200相手100'),
        widget=widgets.RadioSelectHorizontal,
        label='あなたと相手が得ることができる得点について、一番いいと感じる配点を選択してください。以下の全ての質問に回答してください。')
    CRT2 = models.CharField(
        choices=('あなた120相手110','あなた270相手100','あなた100相手300'),
        widget=widgets.RadioSelectHorizontal,
        )
    CRT3 = models.CharField(
        choices=('あなた400相手500','あなた300相手300','あなた200相手100'),
        widget=widgets.RadioSelectHorizontal,
       )
    CRT4 = models.CharField(
        choices=('あなた80相手110','あなた200相手210','あなた80相手70'),
        widget=widgets.RadioSelectHorizontal,
        )
    CRT5 = models.CharField(
        choices=('あなた300相手250','あなた240相手240','あなた100相手50'),
        widget=widgets.RadioSelectHorizontal,
       )




# PAGES
class Q1(Page):
    form_model = 'player'
    form_fields = ['Gender']



class Q2(Page):
    form_model = 'player'
    form_fields = ['CRT1','CRT2','CRT3','CRT4','CRT5',]



page_sequence = [Q1, Q2,]
