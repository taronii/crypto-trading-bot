#!/usr/bin/env python3
"""
セットアップ確認スクリプト
必要なモジュールと設定が正しくインストールされているか確認
"""

import sys
import os

def test_setup():
    print("=" * 60)
    print("Genius Trading System - セットアップ確認")
    print("=" * 60)
    
    # 1. 必要なモジュールのチェック
    print("\n1. モジュールチェック:")
    
    modules = {
        'pybit': 'Bybit API',
        'dotenv': '環境変数管理',
        'numpy': '数値計算',
        'pytz': 'タイムゾーン'
    }
    
    all_ok = True
    for module, description in modules.items():
        try:
            if module == 'dotenv':
                import dotenv
            else:
                __import__(module)
            print(f"  ✅ {module:10} - {description}")
        except ImportError:
            print(f"  ❌ {module:10} - {description} (未インストール)")
            all_ok = False
    
    # 2. 環境変数のチェック
    print("\n2. 環境変数チェック:")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if api_key and api_secret:
            print(f"  ✅ BYBIT_API_KEY    - 設定済み ({len(api_key)}文字)")
            print(f"  ✅ BYBIT_API_SECRET - 設定済み ({len(api_secret)}文字)")
        else:
            print("  ❌ API認証情報が設定されていません")
            all_ok = False
    except Exception as e:
        print(f"  ❌ 環境変数の読み込みエラー: {e}")
        all_ok = False
    
    # 3. ファイル構造のチェック
    print("\n3. ファイル構造チェック:")
    
    files = {
        'genius_multi_trading_v2.py': 'メイン取引システム',
        'services/__init__.py': 'サービスモジュール',
        'services/bybit_service.py': 'Bybit APIサービス',
        '.env': '環境設定',
        'requirements.txt': '依存関係'
    }
    
    for file, description in files.items():
        if os.path.exists(file):
            print(f"  ✅ {file:30} - {description}")
        else:
            print(f"  ❌ {file:30} - {description} (見つかりません)")
            all_ok = False
    
    # 4. Bybit接続テスト
    print("\n4. Bybit接続テスト:")
    
    try:
        from services.bybit_service import BybitService
        
        bybit = BybitService(
            api_key=api_key,
            api_secret=api_secret,
            testnet=False
        )
        
        # サーバー時間を取得してみる
        ticker = bybit.get_ticker('BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            print(f"  ✅ Bybit接続成功 - BTC価格: ${float(ticker['lastPrice']):,.2f}")
        else:
            print("  ❌ Bybit接続は成功しましたが、データ取得に失敗")
            
    except Exception as e:
        print(f"  ❌ Bybit接続エラー: {e}")
        all_ok = False
    
    # 結果
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ すべてのチェックが成功しました！")
        print("\n実行コマンド:")
        print("  python3 genius_multi_trading_v2.py")
    else:
        print("❌ 一部のチェックが失敗しました。")
        print("\nセットアップ手順:")
        print("  1. pip3 install -r requirements.txt")
        print("  2. .envファイルにAPI認証情報を設定")
        print("  3. 再度このスクリプトを実行")
    
    print("=" * 60)

if __name__ == "__main__":
    test_setup()