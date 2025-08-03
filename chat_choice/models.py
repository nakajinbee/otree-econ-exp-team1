from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = "chat_choice"
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 14
    E_CHOICES = list(range(16, 38, 2))  # 16~36の偶数
    Q_CHOICES = [2, 4, 6, 8, 10]
    CHAT_CHOICES = [("C", "C：協力する"), ("N", "N：協力しない")]  # チャット選択肢


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number <= 7:
            self.group_randomly(fixed_id_in_group=True)
        else:
            self.group_randomly()


class Group(BaseGroup):
    total_e = models.IntegerField()
    chat_log_team1 = models.LongStringField(
        blank=True, default=""
    )  # チーム1用チャットログ
    chat_log_team2 = models.LongStringField(
        blank=True, default=""
    )  # チーム2用チャットログ
    force_terminate = models.BooleanField(initial=False)
    P1 = models.FloatField()
    P2 = models.FloatField()

    # team全員がC：協力するを選択しているか判定する
    def is_cooperation_established_for_team(self, team_number):
        team_players = [p for p in self.get_players() if p.team() == team_number]
        # 全員が "C" を選択しているか判定
        return all(
            p.chat_choice == "C" for p in team_players if p.chat_choice is not None
        )

    # 各市場ごとの需要を出すのにEの合計を出す
    def get_team_e_total(self, team_number):
        return sum(
            p.e
            for p in self.get_players()
            if p.team() == team_number and p.e is not None
        )

    def get_group_e_total(self):
        return sum(p.e for p in self.get_players() if p.e is not None)

    # eを選択した後にGroupごとに計算したい処理を実装する
    def sample_calculate_after_select_e(self):
        # TODO:Groupごとに計算したい処理をここに実装する
        team_e_total = self.group.get_team_e_total(self.player.team())
        group_e_total = self.group.get_group_e_total()
        market_share = (
            (36 * team_e_total / group_e_total) * 100 if group_e_total != 0 else 0
        )

        return {"market_share": market_share}

        # TODO:メソッド名も適宜変更する

    # 各グループのpayoffを計算するメソッド
    # 引数のselfはGroup
    def set_payoffs(self):
        players = self.get_players()
        total_e = sum(p.e for p in players)

        e1, e2, e3, e4 = players[0].e, players[1].e, players[2].e, players[3].e
        q1, q2, q3, q4 = players[0].q, players[1].q, players[2].q, players[3].q

        e12 = e1 + e2
        e34 = e3 + e4
        q12 = q1 + q2
        q34 = q3 + q4

        if e12 > 0:
            self.P1 = max(0, 36 - (total_e / e12) * q12)
        else:
            self.P1 = 0

        if e34 > 0:
            self.P2 = max(0, 36 - (total_e / e34) * q34)
        else:
            self.P2 = 0

        for p in players:
            price = self.P1 if p.market() == 1 else self.P2
            raw_profit = price * p.q - p.e
            p.profit = max(0, raw_profit)  # マイナスなら0に
            p.payoff = p.profit


class Player(BasePlayer):
    chat_choice = models.StringField(choices=C.CHAT_CHOICES, blank=True)
    e = models.IntegerField(choices=C.E_CHOICES)
    q = models.IntegerField(choices=C.Q_CHOICES)
    profit = models.FloatField()
    chat_log = models.LongStringField(blank=True, default="")
    timed_out = models.BooleanField(initial=False)

    def market(self):
        return 1 if self.id_in_group in [1, 2] else 2

    def team(self):
        return 1 if self.id_in_group in [1, 2] else 2

    # チャットを送信するメソッド
    def live_chat(self, message):
        team = self.team()
        group = self.group
        label = self.participant.label or f"P{self.id_in_group}"
        text = f"{label}: {message}"
        print(
            f"[live_chat] player {self.id_in_group} (team {team}) sent message: {text}"
        )

        # チャットログをグループで記録
        if team == 1:
            if group.chat_log_team1:
                group.chat_log_team1 += f"\n  {text}"
            else:
                group.chat_log_team1 = text
        else:
            if group.chat_log_team2:
                group.chat_log_team2 += f"\n  {text}"
            else:
                group.chat_log_team2 = text

        # 同じチームの全プレイヤーに送信（return形式）
        return {p.id_in_group: text for p in group.get_players() if p.team() == team}


# E値が入力されずタイムアウトした場合、強制終了する。
def check_timeout_and_missing_e(group: Group, **kwargs):
    # 引数がSubsessionやRoundなどの情報を含む場合があるため、kwargsを使用
    # TODO: 引数の型（Group or Subsession等々）によって適切にチェックする
    for p in group.get_players():
        print(f"p.timed_out {p.timed_out} , p.e {p.e}")

        if p.timed_out and p.e == 0:
            group.force_terminate = True
            break


# Q値が入力されずタイムアウトした場合、強制終了する。
def check_timeout_and_missing_q(group: Group, **kwargs):
    for p in group.get_players():
        print(f"p.timed_out {p.timed_out} , p.q {p.q}")
        if p.timed_out and p.q == 0:
            group.force_terminate = True
            break
