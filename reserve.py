import random
import slackweb
import datetime

from config import Config
from enum import IntEnum, auto
from selenium import webdriver
from selenium.webdriver.common.by import By

class Slack:
    def __init__(self):
        self.slack = slackweb.Slack(url=Config.slack_url)
    
    
    def displayMsg(self, msg=None):
        self.slack.notify(text=msg)


# 曜日を取得する関数
class Week(IntEnum):
    Monday = 0
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()
    Saturday = auto()
    Sunday = auto()
    
    @classmethod
    def ret_week(self, week_number, slack):
        # 曜日の判定と出力
        if Week.Monday == week_number:
            return "月"
        elif Week.Tuesday == week_number:
            return "火"
        elif Week.Wednesday == week_number:
            return "水"
        elif Week.Thursday == week_number:
            return "木"
        elif Week.Friday == week_number:
            return "金"
        elif Week.Saturday == week_number:
            return "土"
        elif Week.Sunday == week_number:
            return "日"
        else:
            slack.displayMsg("存在しない曜日を指定しています.確認してください.")
        
class ClassTime:
    @classmethod
    def ret_class_name(self, times_of_day, slack):
        if times_of_day == 9:
            return "1時限　09:10"
        elif times_of_day == 10:
            return "2時限　10:10"
        elif times_of_day == 11:
            return "3時限　11:10"
        elif times_of_day == 13:
            return "4時限　13:00"
        elif times_of_day == 14:
            return "5時限　14:00"
        elif times_of_day == 15:
            return "6時限　15:00"
        elif times_of_day == 16:
            return "7時限　16:00"
        elif times_of_day == 17:
            return "8時限　17:10"
        elif times_of_day == 18:
            return "9時限　18:10"
        elif times_of_day == 19:
            return "10時限　19:10"
        else:
            slack.displayMsg("存在しない時刻を指定しています.確認してください.")
            
class GET_AMAUTI:
    def __init__(self, month, day, times_of_day, trainer=None, slack=None):
        self.month = month
        self.day = day
        self.w = None
        self.times_of_day = times_of_day
        self.trainer = trainer
        
        self.flag = 1
        
        self.URL = Config.school_url
        self.ID= Config.school_id
        self.PASSWORD = Config.school_pass
        
        self.driver = webdriver.Chrome(executable_path=Config.chrome_driver_path)
        self.slack = slack
        
    def __set_url(self, url):
        self.driver.get(self.URL)

        
    def __set_login_id(self, id_):
        self.login_id = self.driver.find_element(by='name', value='student_cd')
        self.login_id.send_keys(id_)
        

    def __set_login_pw(self, pass_):
        self.login_pw = self.driver.find_element(by='name', value='password')
        self.login_pw.send_keys(pass_)
        
        
    def __click_login_btn(self):
        self.login_btn = self.driver.find_element(by='xpath', value='/html/body/center/form/input[1]')
        self.login_btn.click()
        
        
    def __click_reserve_menu(self):
        self.reserve_menu = self.driver.find_element(by='xpath', value='/html/body/center/table[2]/tbody/tr/td[1]/table[2]/tbody/tr[4]/td/input')
        self.reserve_menu.click()
        
        
    def __click_reserve_date(self):
        month, day, week = self.__ret_formatter_date(self.month, self.day)
        week = Week.ret_week(week, self.slack)
        self.w = week
        
        if self.flag:
            try:
                btn_name = "//input[@value='{}/{}({})']".format(month, day, week)
                reserve_data_btn = self.driver.find_element(by='xpath', value=btn_name)
                reserve_data_btn.click()
            except:
                self.slack.displayMsg("希望の日時が見つかりませんでした.")
                self.flag = 0
        
        
    def __click_class(self):
        class_name = ClassTime.ret_class_name(times_of_day=self.times_of_day, slack=self.slack)
        
        if self.flag:
            try:
                reserve_class_btn = self.driver.find_element(by='xpath', value="//input[@value='{}']".format(class_name))
                reserve_class_btn.click()
            except:
                self.slack.displayMsg("希望の時刻のクラスが見つかりませんでした.")
                self.flag = 0
        
        
    def __click_trainer(self):
        
        if self.flag:
            try:
                reserve_trainer_btn = self.driver.find_element(by='xpath', value="//input[@value='{}']".format(self.trainer))
                reserve_trainer_btn.click()
            except:
                self.slack.displayMsg("トレーナーの方が見つかりませんでした.")
                self.flag = 0
            
            
    def __click_reserve_btn(self):
        
        if self.flag:
            try:
                reserve_btn = self.driver.find_element(by='xpath', value="//input[@value='予約する']")
                reserve_btn.click()
            except:
                self.slack.displayMsg("予約ボタンを押す直線でエラー")
                self.flag = 0
            
            
    def __ret_formatter_date(self, month, day):
        year = datetime.datetime.now().year
        week = datetime.date(year, month, day).weekday()
        return month, day, week
        
        
    def __reset(self):
        try:
            self.__set_url(self.URL)
            self.__set_login_id(id_="")
            self.__set_login_pw(pass_="")
        except:
            self.slack.displayMsg("ログイン画面に戻れませんでした.")
            
            
    def __goal(self):
        self.slack.displayMsg("予約完了しました!!")
        self.slack.displayMsg("{}/{}/({}): {}　{}～".format(self.month, self.day, self.w, self.trainer, ClassTime.ret_class_name(self.times_of_day, self.slack)))
        
        
    def reserve(self):
        self.__reset()
        self.__set_url(self.URL)
        self.__set_login_id(self.ID)
        self.__set_login_pw(self.PASSWORD)
        self.__click_login_btn()
        self.__click_reserve_menu()
        
        self.__click_reserve_date()
        self.__click_class()
        self.__click_trainer()
        
        try:
            self.__click_reserve_btn()
            if self.flag:
                self.__goal()
                return True
        except:
            self.slack.displayMsg("なんらかのエラーで予約が取れませんでした.")
                        
        return False

import time

def main():
    is_finished = False

    count = 0

    slack = Slack()

    while(True):
        now_time = datetime.datetime.now().hour

        if now_time==Config.start_reserve and count==0:
            time.sleep(Config.sleep_time)
            slack.displayMsg("これから予約を開始します.")

        if now_time == Config.start_reserve:
            slack = Slack()
            booking = GET_AMAUTI(month=Config.month, day=Config.day, times_of_day=Config.times_of_day, trainer=Config.trainer, slack=slack)
            is_finished = booking.reserve()

        if is_finished:
            break

        time.sleep(sleep_time)

    print("正常に終了しました")
    
if __name__ == "__main__":
    main()
