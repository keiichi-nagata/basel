# SOP — 週次締め（毎週月曜）＋ 月次締め

## 週次（15〜30分）

1. **数字を集める**
   - `marketing/threads/log.csv` に前週の投稿実績を記入
   - 各開発部の `published/` から前週公開分の初速メモを回収
   - ASP管理画面（A8）でクリック・確定を確認
2. **`finance/kpi.csv` に1行追加**（週= `YYYY-Www`）
3. **ファネルの率を計算**
   ```
   プロフ訪問率 = profile_visits / threads_impressions
   note遷移率   = note_views / profile_visits
   フォロー率   = new_followers / note_views
   収益転換率   = (paid_note_sales_count + affiliate_conversions) / note_views
   ```
4. **最小の率がボトルネック** → `STATE.md` の「今週の焦点」に打ち手を1〜2個書く
5. **STATE.md を更新**（資産インベントリ、ブロッカー、今週のチェックリスト）
6. **企画部**: `planning/ideas.md` を見て、採用/保留/却下を1件は動かす
7. git コミット（「weekly: YYYY-Www」）

## 月次（月初、+30分）

1. 前月の `finance/ledger.csv` を締める
2. 会計ソフトと突合（売上・経費の漏れ確認）
3. `finance/reports/YYYY-MM.md` を作成:
   - 売上（paid_note / affiliate / other）、経費（カテゴリ別）、利益
   - KPI推移（4〜5週分の率の折れ線）
   - 各マガジンの成績（閲覧・フォロー増・アフィリ）
   - 「中止・撤退の基準」に触れるマガジンがないか（`docs/roadmap-90days.md`）
   - 次月の打ち手 3つ
4. 3ヶ月連続で黒字かつ規模が伸びていれば、法人化メモを `docs/decisions/` に起票（当面は個人事業）
