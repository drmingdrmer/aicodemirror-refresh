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


        # Preloaded data
        self.credit_info = None
        self.recover_info = None
        self.reset_info = None
        self.recover_rate = None

    def load(self):
        """Preload all necessary information from API"""
        print("=== 开始加载用户信息 ===")
        self.credit_info = self._make_request("GET", self.credit_info_api, "获取积分信息")
        self.recover_info = self._make_request("GET", self.recover_rate_api, "获取积分恢复信息")
        self.reset_info = self._make_request("GET", self.credit_reset_api, "获取积分重置信息")
        self.recover_rate = int(self.recover_info['recoveryRate'])
        print("=== 用户信息加载完成 ===\n")

    def load_status(self):
        """Print current account status"""
        if not self.credit_info:
            self.load()

        current_user = self.credit_info['userId']
        current_plan = self.credit_info['plan']
        current_credit = self.credit_info['credits']
        print(f"\n当前用户：{current_user}")
        print(f"当前计划：{current_plan}")
        print(f"当前积分：{current_credit}")
        print(f"积分恢复率：{self.recover_rate}/小时")

        remain_reset_count = self.reset_info['remainingResets']
        print(f"剩余重置次数：{remain_reset_count}")

    def check(self):
        print("\n=== 检查账户状态 ===")
        self.load_status()

        # Write NDJSON line
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        record = {
            "timestamp": timestamp,
            "credits_left": self.credit_info['credits']
        }

        with open("credits_history.ndjson", "a") as f:
            f.write(json.dumps(record) + "\n")


    def _make_request(self, method, url, description):
        """Make HTTP request with detailed logging"""
        print(f"正在{description}: {url}")
        if method == "GET":
            r = self.session.get(url, headers={"cookie": self.cookies})
        elif method == "POST":
            r = self.session.post(url, headers={"cookie": self.cookies})
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        print(f"响应状态码: {r.status_code}")
        if r.status_code != 200:
            print(f"{description}失败")
            print(f"响应内容: {r.text}")
            exit(1)

        data = r.json()
        print(f"{description}结果: {json.dumps(data, indent=2)}")
        return data

    def status(self):
        print("\n=== 查看状态（不执行重置） ===")
        self.load_status()

        if self.reset_info['remainingResets'] <= 0:
            print("\n已无重置次数，请等待积分恢复")
        else:
            print("\n可以执行积分重置")

    def refresh(self):
        print("\n=== 开始刷新积分 ===")
        self.load_status()

        if self.reset_info['remainingResets'] <= 0:
            print("\n已无重置次数，请等待积分恢复")
            return

        print("\n开始执行积分重置...")
        self._make_request("POST", self.credit_reset_api, "执行积分重置")
        print("\n=== 积分刷新完成 ===")


def main():
    parser = argparse.ArgumentParser(description='AiCodeMirror credit management')
    parser.add_argument('command', choices=['refresh', 'check', 'status'],
                       help='Command to execute: refresh (reset credits), check (display and log status), status (check without reset)')

    args = parser.parse_args()

    client = AiCodeMirrorClient()

    if args.command == 'refresh':
        client.refresh()
    elif args.command == 'check':
        client.check()
    elif args.command == 'status':
        client.status()


if __name__ == '__main__':
    main()
