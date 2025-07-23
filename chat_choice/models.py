from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'chat_choice'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 14
    E_CHOICES = list(range(16,38,2)) #16~36の偶数
    Q_CHOICES = [2,4,6,8,10]

class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number <= 7:
            self.group_randomly(fixed_id_in_group=True)
        else:
            self.group_randomly()    

class Group(BaseGroup):
    total_e = models.IntegerField()
    P1 = models.FloatField()
    P2 = models.FloatField()
    chat_log_team1 = models.LongStringField(blank=True, default='')  # チーム1用チャットログ
    chat_log_team2 = models.LongStringField(blank=True, default='')  # チーム2用チャットログ
    force_terminate = models.BooleanField(initial=False) 

class Player(BasePlayer):
    chat_choice = models.StringField(choices=[('C', 'C'), ('N', 'N')], blank=True
    )
    e = models.IntegerField(choices=C.E_CHOICES)
    q = models.IntegerField(choices=C.Q_CHOICES)
    profit = models.FloatField()
    chat_log = models.LongStringField(blank=True, default='')
    timed_out = models.BooleanField(initial=False)


    def market(self):
        return 1 if self.id_in_group in [1,2] else 2

    def team(self):
        return 1 if self.id_in_group in [1, 2] else 2
    
    def live_chat(self, message):
        team = self.team()
        group = self.group
        label = self.participant.label or f"P{self.id_in_group}"
        text = f"{label}: {message}"
        print(f"[live_chat] player {self.id_in_group} (team {team}) sent message: {text}")

    # チャットログをグループで記録
        if team == 1:
            if group.chat_log_team1:
                group.chat_log_team1 += f"\n{text}"
            else:
                group.chat_log_team1 = text
        else:
            if group.chat_log_team2:
                group.chat_log_team2 += f"\n{text}"
            else:
                group.chat_log_team2 = text

        debug_chat = ""
        if team == 1:
            debug_chat = chat_log_team1
        else: 
            debug_chat = chat_log_team2
        print(f"[live_chat] player {self.id_in_group} (team {team}) sent message: {text} group.chat_log_team1")

    # 同じチームの全プレイヤーに送信（return形式）
        return {p.id_in_group: text for p in group.get_players() if p.team() == team}
    

def check_force_terminate(group: Group, **kwargs):
    for p in group.get_players():
        if p.timed_out or p.e is None or p.q is None:
            group.force_terminate = True
            break 
    

def set_payoffs(group: Group):
    players = group.get_players()
    total_e = sum(p.e for p in players)

    e1, e2, e3, e4 = players[0].e, players[1].e, players[2].e, players[3].e
    q1, q2, q3, q4 = players[0].q, players[1].q, players[2].q, players[3].q

    e12 = e1 + e2
    e34 = e3 + e4
    q12 = q1 + q2
    q34 = q3 + q4
    
    if e12 > 0:
        group.P1 = max(0, 36 - (total_e / e12) * q12)
    else:
        group.P1 = 0

    if e34 > 0:
        group.P2 = max(0, 36 - (total_e / e34) * q34)
    else:
        group.P2 = 0

    for p in players:
        price = group.P1 if p.market() == 1 else group.P2
        raw_profit = price * p.q - p.e
        p.profit = max(0, raw_profit)  # マイナスなら0に
        p.payoff = p.profit