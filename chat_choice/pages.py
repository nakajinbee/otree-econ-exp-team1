from otree.api import Page, WaitPage
from .models import check_force_terminate, set_payoffs


class ChatPage(Page):
    live_method = 'live_chat'
    form_model = 'player'
    form_fields = ['chat_choice']
    timeout_seconds = 45


    def before_next_page(self):
        if self.timeout_happened and not self.player.chat_choice:
            self.player.chat_choice = 'N'


class EChoice(Page):
    form_model = 'player'
    form_fields = ['e']
    timeout_seconds = 30

    def before_next_page(self):
        if self.timeout_happened or self.player.e is None:
            self.player.timed_out = True



class QChoice(Page):
    form_model = 'player'
    form_fields = ['q']
    timeout_seconds = 30

    def before_next_page(self):
        if self.timeout_happened or self.player.q is None:
            self.player.timed_out = True       


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class CheckTimeout(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = check_force_terminate


class Results(Page):
    timeout_seconds = 10  

    def is_displayed(self):
        return not self.group.force_terminate


    def vars_for_template(self):
        return {
            'price': self.player.group.P1 if self.player.market() == 1 else self.player.group.P2,
            'profit': self.player.profit,
            'chat_log': self.player.chat_log,
        }    


class ForcedTermination(Page):
    def is_displayed(self):
        return self.group.force_terminate

    def vars_for_template(self):
        return {
            'message': "1人以上が時間内に選択できなかったため、全員強制終了となりました。"
        }
    
page_sequence = [ChatPage, EChoice, QChoice, CheckTimeout, ResultsWaitPage, Results, ForcedTermination,]