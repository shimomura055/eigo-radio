# 委任_04(Phase A / W4): 最終Human報告用資料(LR=赤・Fallback=濃い青)の設計(全Family・全Level・全Role)(API 0)

共通事項=`…_委任_00_COMMON.md`(必読)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W4_FINAL_HUMAN_REPORT_DESIGN_01.md`+表示サンプル`W4_SAMPLE_01.html`(静的・保存データから手作りでよい。公開dirには置かない)。**設計のみ(Productionコード変更禁止)**。Opus条件Aレビュー対象。

## ユーザー決定(原文§2・§6、再質問しない)
- 赤/濃青の表示・注記・変更履歴は、TTS・ASR・組立完了後の**ユーザー最終確認資料のみ**。制作スクリプト・TTS入力・ASR正解原稿・学習者向け公開本文・KP/KW/文法の学習用表示・Style Promptへ混入禁止。注記は読み上げない。
- A. LR: 変更箇所を赤色。必須=LR発動の事実・対象音声区間・変更前英文・変更後英文・変更語句。
- B. Fallback: 対象テキスト全体と注記を濃い青色。必須=Fallback発動の事実・最終採用音声のStyle名・通常Styleから何へ切替わったか・適用区間/Chunk/本文範囲。対象=英語短文Style(Minimal)・日本語短文Style(Minimal)・ENGLISH_LOCK・Z Dialogue Style切替・その他承認済みFallbackで実際にStyleが変わった採用音声。Styleが変わらない再試行は表示しない。
- C. 重複: 両方表示、色の意味を混同させない、区間全体と変更語句を識別、実行履歴と最終採用状態を区別。**採用されなかった試行のFallbackを最終採用Styleとして誤表示しない**。開始/終了時刻等の技術情報は不要。
- 対象Family: X/Y/Z全Role+A/B/C等既存Familyの「適用可能な最終Human報告仕様」(音声生成方式は置換しない)。

## 設計すべき事項
1. **既存の人間確認資料の棚卸し**(Family別): X HR試聴ページ(`hr_02`等の生成器)、Y試聴節、Z `review_request.md`/試聴ページ、`user_test/human_review.html`、`pass_with_warning_listening_list.json`、各Familyの最終報告テンプレ。どれを「最終Human報告用資料」として拡張するか/新設するか(1 run=1資料、Std/Adv別、全Role[本文・topic_intro・comment・in_one_line・Preview・KP英語・KP解説・日本語音声・Z Dialogue]を網羅)。生成タイミング(assemble/pages後、公開ページとは別dir)。
2. **データ源**: W1(委任_01)が棚卸す記録を前提に、最終採用attemptのLR/Fallback状態を確定する読取規則(採用attempt以外のFallbackを除外する規則、LR+Fallback重複時のStyle名=LR後blockの採用attempt)。記録欠落時の表示(「記録なし」と明示、推測しない)。
3. **表示仕様**: 赤=LR変更語句(前後英文を併記、差分語句の強調)、濃青=Fallback対象テキスト全体+注記。両者重複時のレイアウト。色のみに依存しない識別(ラベル文字併記)。日本語音声Fallback(JA minimal)の表示。Chunk/区間の対応表示。技術情報(時刻等)は非表示。
4. **混入防止の構造的保証**: 資料生成器が公開ページ・TTS・ASR・KP表示・Promptのコードパスと共有しない(読み取り専用の後処理)ことの設計と、混入検知test(公開HTML・TTS入力・ASR期待文・Style Promptに注記文字列・色class・LR注記が含まれない)。
5. **A/B/C等既存Familyへの適用**: 記録構造の有無で「適用可能/記録不足で表示不可(その旨を資料に明記)」を判定。音声生成方式は変えない。
6. **既公開4件+告げ口心臓**への適用例: 保存データから、AI島Std/Adv(LR赤)、Word Gacha Adv、メロスAdv、猿の手Std、Y E-1(Fallback/人間承認原文)、告げ口心臓(LR 0/Fallback 0=「発動なし」表示)のサンプルを`W4_SAMPLE_01.html`に手作りし、表示の妥当性を示す。
7. **test計画**: 生成器の単体(採用attempt判定・重複・欠落)、混入検知、Family別integration。

## 出力形式
表+file:line+サンプルHTML。判断候補A/B/C/D区分。
