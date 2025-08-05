# 🚀 X Server VPS クイックセットアップガイド

## 📱 ステップ1: Xserver VPS登録（10分）

1. **公式サイトアクセス**
   - https://vps.xserver.ne.jp/
   - 「お申し込み」クリック

2. **プラン選択**
   ```
   推奨: 2GBプラン（月額1,900円）
   OS: Ubuntu 22.04 LTS
   ```

3. **支払い**
   - クレジットカード推奨
   - 即時利用開始可能

## 🔐 ステップ2: VPS情報をメモ

登録完了後、以下をメモ：
```
IPアドレス: xxx.xxx.xxx.xxx
rootパスワード: ************
```

## 💻 ステップ3: ボットのデプロイ（5分）

### Mac/Linuxの場合

1. **ターミナルを開く**

2. **プロジェクトフォルダに移動**
   ```bash
   cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean
   ```

3. **デプロイスクリプトを編集**
   ```bash
   nano deploy_to_vps.sh
   ```
   
   7行目のIPアドレスを変更：
   ```bash
   VPS_IP="あなたのVPSのIPアドレス"
   ```
   
   保存: Ctrl+X → Y → Enter

4. **自動デプロイ実行**
   ```bash
   ./deploy_to_vps.sh
   ```

5. **パスワード入力**
   - 何度か聞かれるので、rootパスワードを入力
   - .envファイルのアップロード確認で`y`を入力

## 🎮 ステップ4: ボット起動（2分）

1. **VPSに接続**
   ```bash
   ssh root@[あなたのVPSのIP]
   ```

2. **ボット起動**
   ```bash
   systemctl start crypto-bot
   ```

3. **動作確認**
   ```bash
   journalctl -u crypto-bot -f
   ```

## ✅ 完了チェックリスト

- [ ] Xserver VPS登録完了
- [ ] IPアドレスとパスワードをメモ
- [ ] deploy_to_vps.shのIP変更
- [ ] デプロイスクリプト実行
- [ ] VPSでボット起動
- [ ] ログで動作確認

## 🆘 トラブルシューティング

### SSH接続できない
```bash
# IPアドレスが正しいか確認
ping [VPSのIP]

# ファイアウォール確認（VPSパネルから）
```

### デプロイスクリプトエラー
```bash
# 手動でSSH接続テスト
ssh root@[VPSのIP]

# 権限確認
chmod +x deploy_to_vps.sh
```

### ボットが起動しない
```bash
# VPS上で手動実行
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate
python3 genius_multi_trading_v2_with_trading.py
```

## 📞 サポート

**Xserver VPSサポート**
- 電話: 06-6147-2580
- 受付: 平日10-18時

---

🎉 **最短15分で24時間自動売買スタート！**