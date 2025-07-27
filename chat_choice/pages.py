from otree.api import Page, WaitPage
from .models import set_payoffs
from .models import check_force_terminate


class ChatPage(Page):
    form_model = "player"
    form_fields = ["chat_choice"]
    timeout_seconds = 45

    def before_next_page(self):
        if self.timeout_happened and not self.player.chat_choice:
            self.player.chat_choice = "N"


# チャットの前の待機ページ
# 全員がC or N　を選択した上でChatのページを開く必要がある
class CooperationChoiceWaitPage(WaitPage):
    # 処理なし
    pass


class EChoice(Page):
    form_model = "player"
    form_fields = ["e"]
    timeout_seconds = 30
    live_method = "live_chat"

    # テンプレート（〜.html）に渡す変数
    def vars_for_template(self):
        is_cooperation = self.group.is_cooperation_established_for_team(
            self.player.team()
        )

        return {
            # チームの協力が確立されているかどうかを判定
            "is_cooperation_established_for_team": is_cooperation,
            "chat_log": (
                self.player.group.chat_log_team1
                if self.player.team() == 1
                else self.player.group.chat_log_team2
            ),
        }

    def before_next_page(self):
        if self.timeout_happened or self.player.e is None:
            self.player.timed_out = True


class MarketShare(Page):
    def vars_for_template(self):
        team_e_total = self.group.get_team_e_total(self.player.team())
        group_e_total = self.group.get_group_e_total()
        market_share = (
            (36 * team_e_total / group_e_total) * 100 if group_e_total != 0 else 0
        )

        return {"market_share": market_share}

    def is_displayed(self):
        return not self.group.force_terminate

    timeout_seconds = 10  # 時間制限あり


class QChoice(Page):
    form_model = "player"
    form_fields = ["q"]
    timeout_seconds = 30

    def before_next_page(self):
        if self.timeout_happened or self.player.q is None:
            self.player.timed_out = True


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class CheckTimeout(WaitPage):
    wait_for_all_groups = True
    # グループ内のプレイヤーがタイムアウトしたかどうかをチェック
    after_all_players_arrive = check_force_terminate


class Results(Page):
    timeout_seconds = 10

    def is_displayed(self):
        return not self.group.force_terminate

    def vars_for_template(self):
        return {
            "price": (
                self.player.group.P1
                if self.player.market() == 1
                else self.player.group.P2
            ),
            "profit": self.player.profit,
            "chat_log": (
                self.player.group.chat_log_team1
                if self.player.team() == 1
                else self.player.group.chat_log_team2
            ),
        }


class ForcedTermination(Page):
    def is_displayed(self):
        return self.group.force_terminate

    def vars_for_template(self):
        return {
            "message": "1人以上が時間内に選択できなかったため、全員強制終了となりました。"
        }


page_sequence = [
    ChatPage,
    CooperationChoiceWaitPage,
    EChoice,
    MarketShare,
    QChoice,
    CheckTimeout,
    ResultsWaitPage,
    Results,
    ForcedTermination,
]
