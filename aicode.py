import requests
import os
import argparse
import json
from datetime import datetime


class AiCodeMirrorClient:
    def __init__(self, cookies_file="aicodemirror_cookies.txt"):
        if not os.path.exists(cookies_file):
            print("请先登录aicodemirror，将cookies写入aicodemirror_cookies.txt")
            open(cookies_file, "w").close()
            exit(1)

        self.session = requests.Session()
        self.session.headers['user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.session.headers['accept'] = "application/json"
        self.cookies = open(cookies_file, "r").read().strip()

        self.api_base_url = "https://www.aicodemirror.com"
        self.credit_info_api = self.api_base_url + "/api/user/credits"
        self.recover_rate_api = self.api_base_url + "/api/user/credit-recovery"
        self.credit_reset_api = self.api_base_url + "/api/user/credit-reset"

        self.morning_hour = 8

        self.plan_credits_map = {
            "PRO": 8000,
            "MAX": 20000,
            "ULTRA": 50000,
        }
        self.recover_rate_map = {
            "PRO": 200,
            "MAX": 500,
            "ULTRA": 1200,
        }
        
        # Preloaded data
        self.credit_info = None
        self.recover_info = None
        self.reset_info = None
        self.recover_rate = None

    def load(self):
        """Preload all necessary information from API"""
        self.credit_info = self.query_credit_info()
        self.recover_info = self.query_recover_rate()
        self.reset_info = self.query_reset_info()
        self.recover_rate = int(self.recover_info['recoveryRate'])

    def check(self):
        if not self.credit_info:
            self.load()
            
        current_user = self.credit_info['userId']
        current_plan = self.credit_info['plan']
        current_credit = self.credit_info['credits']
        print(f"当前用户：{current_user}，当前计划：{current_plan}，当前积分：{current_credit}")
        
        print(f"积分恢复率：{self.recover_rate}/小时")
        
        remain_reset_count = self.reset_info['remainingResets']
        print(f"剩余重置次数：{remain_reset_count}")
        
        # Write NDJSON line
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        record = {
            "timestamp": timestamp,
            "credits_left": current_credit
        }
        
        with open("credits_history.ndjson", "a") as f:
            f.write(json.dumps(record) + "\n")


    def refresh_by_policy(self):
        if not self.credit_info:
            self.load()
            
        current_user = self.credit_info['userId']
        current_plan = self.credit_info['plan']
        current_credit = self.credit_info['credits']
        print(f"当前用户：{current_user}，当前计划：{current_plan}，当前积分：{current_credit}")

        print(f"积分恢复率：{self.recover_rate}/小时")

        remain_reset_count = self.reset_info['remainingResets']
        print(f"剩余重置次数：{remain_reset_count}")
        if remain_reset_count <= 0:
            print("已无重置次数，请等待积分恢复")
            return

        if current_credit < self.recover_rate:
            print("积分过低，直接重置")
            self.do_reset()
            return

        now = datetime.now()
        if now.hour == 23 and now.minute > 30:
            print("已超过23点30分，尝试恢复")
            if self.plan_credits_map.get(current_plan, 0) > (current_credit + self.morning_hour * self.recover_rate):
                self.do_reset()
                return
            else:
                print("积分可自动恢复，无需重置")


    def query_credit_info(self):
        r = self.session.get(self.credit_info_api, headers={
            "cookie": self.cookies
        })
        if r.status_code != 200:
            print("获取积分信息失败")
            exit(1)
        return r.json()

    def query_recover_rate(self):
        r = self.session.get(self.recover_rate_api, headers={
            "cookie": self.cookies
        })
        if r.status_code != 200:
            print("获取积分恢复信息失败")
            exit(1)
        return r.json()

    def query_reset_info(self):
        r = self.session.get(self.credit_reset_api, headers={
            "cookie": self.cookies
        })
        if r.status_code != 200:
            print("获取积分重置信息失败")
            exit(1)
        return r.json()

    def do_reset(self):
        r = self.session.post(self.credit_reset_api, headers={
            "cookie": self.cookies
        })
        if r.status_code != 200:
            print("积分重置失败")
            exit(1)
        return r.json()


def main():
    parser = argparse.ArgumentParser(description='AiCodeMirror credit management')
    parser.add_argument('command', choices=['refresh', 'check'], 
                       help='Command to execute: refresh (manage credits) or check (display status)')
    
    args = parser.parse_args()
    
    client = AiCodeMirrorClient()
    
    if args.command == 'refresh':
        client.refresh_by_policy()
    elif args.command == 'check':
        client.check()


if __name__ == '__main__':
    main()
