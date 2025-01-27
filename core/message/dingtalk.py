from dataclasses import dataclass

from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard, CardItem

from core.utils.ip import get_host_ip


@dataclass
class DingTalkDict:
    webhook: str
    secret: str


class DingtalkMessageBase:
    def __init__(self, dingtalk_dict: DingTalkDict):
        if not dingtalk_dict.secret:
            raise ValueError("dingtalk_dict must contain webhook and secret")
        self.bot = DingtalkChatbot(dingtalk_dict.webhook, dingtalk_dict.secret)

    def send_text_message(self, msg):
        return self.bot.send_text(msg=msg)

    def new_btn(self, title, url):
        return CardItem(title, url)

    def send_card_action_message(self, title, text, btns):
        ac = ActionCard(title=title,
                        text=text,
                        btns=btns,
                        btn_orientation=1,
                        hide_avatar=1)

        return self.bot.send_action_card(ac)

    def send_markdown_message(self, title, text, is_at_all=False, at_mobiles=[], at_dingtalk_ids=[], is_auto_at=True):
        return self.bot.send_markdown(title=title, text=text, is_at_all=is_at_all, at_mobiles=at_mobiles,
                                      at_dingtalk_ids=at_dingtalk_ids, is_auto_at=is_auto_at)


class SendInterfaceAutoTest(DingtalkMessageBase):
    def send_dingtalk_autotest_result(self, total, run, skip, success, failure, html_report_url=None):
        title = "自动化测试"
        success_picture = "https://sa.ibrolive.com/test/success.png"
        error_picture = "https://sa.ibrolive.com/test/error.png"

        text = f"![选择]({success_picture if failure == 0 else error_picture}) \n" \
               f"#### 设备参数: \n" \
               f"IP: **{get_host_ip()}** \n" \
               f"#### 运行结果: \n" \
               f"<span style='color: blue;'>总数: **{total}**</span>, " \
               f"<span style='color: green;'>运行: **{run}**</span>, " \
               f"<span style='color: orange;'>跳过: **{skip}**</span>, " \
               f"<span style='color: darkgreen;'>成功: **{success}**</span>, " \
               f"<span style='color: red;'>失败: **{failure}**</span>"

        if html_report_url:
            btn_list = [self.new_btn("点击查看报告详情", html_report_url)]
            self.send_card_action_message(title, text, btn_list)
        else:
            self.send_markdown_message(title=title, text=text)


class SendBugMessage(DingtalkMessageBase):

    def send_dingtalk_bug_message(self, bug_num, bug_title, bug_url, bug_status, at_mobiles):
        """
        :param bug_num:  bug编号
        :param bug_title: bug标题
        :param bug_url: bug详情页面url
        :param bug_status: bug状态
        :param at_mobiles: bug @人员的手机号列表   list[int]
        :return:
        """
        title = "pingcode bug 通知"
        text = f" ###### [BUG编号]：__{bug_num}__<br>" \
               f"[BUG标题]：[{bug_title}]({bug_url})<br>" \
               f"[BUG状态]：__{bug_status}__<br> "

        self.send_markdown_message(title=title, text=text, at_mobiles=at_mobiles)
