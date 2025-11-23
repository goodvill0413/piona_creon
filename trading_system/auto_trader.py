"""
자동매매 실행 시스템
- 매수/매도 신호 실행
- 포지션 관리
- 손절가/목표가 관리
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


class AutoTrader:
    """자동매매 실행 시스템"""

    def __init__(self, mode='simulation'):
        """
        Parameters:
            mode: 'simulation' (모의매매) 또는 'real' (실전매매)
        """
        self.name = "Auto Trader"
        self.mode = mode
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        os.makedirs(self.db_path, exist_ok=True)

        # 포지션 로드
        self.positions = self._load_positions()

        # 실행 로그
        self.execution_log = []

    def execute_signal(self, code, final_decision, stock_info):
        """
        매매 신호 실행

        Parameters:
            code: 종목코드
            final_decision: 최종 결정 (from ScoreCalculator)
            stock_info: 종목 정보 (현재가, 손절가, 목표가 등)

        Returns:
            dict: 실행 결과
        """
        action = final_decision['final_signal']['action']
        trading_mode = final_decision['trading_mode']
        total_score = final_decision['total_score']

        # 현재 포지션 확인
        current_position = self.positions.get(code)

        # 매수 신호
        if action in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
            if current_position is None:
                result = self._execute_buy(code, stock_info, trading_mode, total_score)
            else:
                result = {
                    "status": "SKIPPED",
                    "reason": "이미 보유 중",
                    "code": code,
                    "action": "HOLD"
                }

        # 매도 신호
        elif action in ['STRONG_SELL', 'SELL', 'WEAK_SELL']:
            if current_position is not None:
                result = self._execute_sell(code, stock_info, "SIGNAL")
            else:
                result = {
                    "status": "SKIPPED",
                    "reason": "보유 종목 아님",
                    "code": code,
                    "action": "NONE"
                }

        # 관망
        else:
            if current_position is not None:
                # 보유 중이면 손절/익절 체크
                result = self._check_exit_conditions(code, current_position, stock_info)
            else:
                result = {
                    "status": "HOLD",
                    "reason": "관망",
                    "code": code,
                    "action": "WAIT"
                }

        # 실행 로그 저장
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "result": result
        })

        return result

    def _execute_buy(self, code, stock_info, trading_mode, score):
        """매수 실행"""
        current_price = stock_info['current_price']
        stop_loss = stock_info.get('stop_loss', current_price * 0.95)
        target_1 = stock_info.get('target_1', current_price * 1.05)
        target_2 = stock_info.get('target_2', current_price * 1.10)

        # 포지션 생성
        position = {
            "code": code,
            "buy_price": current_price,
            "buy_date": datetime.now().isoformat(),
            "trading_mode": trading_mode,
            "score": score,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "quantity": 100,  # 임시 수량 (실전에서는 자금 관리 적용)
            "status": "OPEN"
        }

        # 시뮬레이션 모드
        if self.mode == 'simulation':
            self.positions[code] = position
            self._save_positions()

            return {
                "status": "SUCCESS",
                "action": "BUY",
                "code": code,
                "price": current_price,
                "quantity": 100,
                "mode": "SIMULATION",
                "trading_mode": trading_mode
            }

        # 실전 모드 (향후 구현)
        else:
            # TODO: Creon API로 실제 매수 주문
            return {
                "status": "NOT_IMPLEMENTED",
                "action": "BUY",
                "reason": "실전 매매 미구현"
            }

    def _execute_sell(self, code, stock_info, reason):
        """매도 실행"""
        current_price = stock_info['current_price']
        position = self.positions.get(code)

        if position is None:
            return {
                "status": "ERROR",
                "reason": "포지션 없음",
                "code": code
            }

        buy_price = position['buy_price']
        profit_pct = (current_price / buy_price - 1) * 100

        # 시뮬레이션 모드
        if self.mode == 'simulation':
            # 매매 이력 저장
            self._save_trade_history(code, position, current_price, profit_pct, reason)

            # 포지션 제거
            del self.positions[code]
            self._save_positions()

            return {
                "status": "SUCCESS",
                "action": "SELL",
                "code": code,
                "buy_price": buy_price,
                "sell_price": current_price,
                "profit_pct": round(profit_pct, 2),
                "reason": reason,
                "mode": "SIMULATION"
            }

        # 실전 모드 (향후 구현)
        else:
            # TODO: Creon API로 실제 매도 주문
            return {
                "status": "NOT_IMPLEMENTED",
                "action": "SELL",
                "reason": "실전 매매 미구현"
            }

    def _check_exit_conditions(self, code, position, stock_info):
        """손절/익절 조건 체크"""
        current_price = stock_info['current_price']
        buy_price = position['buy_price']
        stop_loss = position['stop_loss']
        target_1 = position['target_1']
        target_2 = position.get('target_2')

        # 손절
        if current_price <= stop_loss:
            return self._execute_sell(code, stock_info, "STOP_LOSS")

        # 1차 목표 달성
        elif current_price >= target_1:
            # 2차 목표가 있으면 일부 익절, 나머지 홀딩
            if target_2 and current_price < target_2:
                return {
                    "status": "PARTIAL_PROFIT",
                    "action": "HOLD",
                    "code": code,
                    "message": "1차 목표 달성, 2차 목표 대기"
                }
            else:
                return self._execute_sell(code, stock_info, "TAKE_PROFIT")

        # 홀딩
        else:
            profit_pct = (current_price / buy_price - 1) * 100
            return {
                "status": "HOLDING",
                "action": "HOLD",
                "code": code,
                "profit_pct": round(profit_pct, 2)
            }

    def _load_positions(self):
        """포지션 로드"""
        position_file = os.path.join(self.db_path, 'positions.json')

        if not os.path.exists(position_file):
            return {}

        try:
            with open(position_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _save_positions(self):
        """포지션 저장"""
        position_file = os.path.join(self.db_path, 'positions.json')

        with open(position_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2)

    def _save_trade_history(self, code, position, sell_price, profit_pct, reason):
        """매매 이력 저장"""
        history_file = os.path.join(self.db_path, 'trading_history.json')

        # 기존 이력 로드
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []

        # 새 거래 추가
        trade = {
            "code": code,
            "buy_date": position['buy_date'],
            "sell_date": datetime.now().isoformat(),
            "buy_price": position['buy_price'],
            "sell_price": sell_price,
            "profit_pct": profit_pct,
            "trading_mode": position['trading_mode'],
            "score": position['score'],
            "reason": reason,
            "quantity": position['quantity']
        }

        history.append(trade)

        # 저장
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_open_positions(self):
        """현재 보유 포지션 조회"""
        return self.positions

    def get_execution_log(self):
        """실행 로그 조회"""
        return self.execution_log
