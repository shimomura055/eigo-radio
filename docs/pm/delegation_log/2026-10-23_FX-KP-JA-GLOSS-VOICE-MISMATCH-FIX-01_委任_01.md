FABLE-DELEGATION-MARKER: FX-KP-JA-GLOSS-VOICE-MISMATCH-FIX-01-委任_01-20261023

# 委任_01: 記事B Standard KP1 日本語意味「定款」clip 1本の個別再生成(A案、ユーザー承認済み)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-JA-GLOSS-VOICE-MISMATCH-FIX-01_委任_01.md`(N≈316〜326、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FX-KP-JA-GLOSS-VOICE-MISMATCH-FIX-01_USER.md` に逐語保存。
3. `docs/pm/ACTIVE_TASK.md`: 別agent(ASR-HOMOPHONE 委任_04)が並行中。編集直前に再読込し、OPEN-460の並行タスク1行だけを本管理IDの状態へ更新(他行は触らない)。**有料呼出の直前に同行へ「有料run進行中(時刻)」、終了後「有料run終了(時刻)」を記す。**

## 1. ユーザー指示原文(逐語)
```
## Claude Codeへの指示:記事B「定款」Voice個別修正

### 1. ユーザー決定

**A案(個別修正)のみ承認します。**

Family X「マスク氏の『良い考え』で、合併話が渋滞する?」StandardのKey Phrase `articles of incorporation` の日本語意味「定款」について、女性Voice(Aoede)として自然に聞こえる音声へ修正してください。

男女の声質差は学習体験に重大な影響を与える問題ではないため、今回は構造的な改善を行いません。

### 2. 実施内容

1. 対象の「定款」clip 1本のみAoedeで再生成。
2. 既存のAoede音声と比較し、声質が自然に一致することを確認。
3. 必要なASR品質検査を実施。
4. 該当clipを差し替え、Standardの通し音声と試聴ページを更新。
5. 公開ページで正しい音声が再生されることを確認。

F0は参考指標とし、170Hz以上を新しい合否基準として固定しないでください。

### 3. Scope・QCD

- 他のclipや本文は変更しない。
- 新しいVoice検査Gateの設計・Trial・Production実装は行わない。
- 必要最小限の再生成で完了させる。
- 既存の品質基準を維持する。
- 既存の再試行上限・費用上限を遵守する。

**本件は個別修正でCloseする方針です。** 将来の包括対策を新しいユーザー判断事項として起票しないでください。

### 4. 完了報告

以下を簡潔に報告してください。

- 修正前後のVoice確認結果
- ASR・音声QA結果
- 更新後の試聴URL
- 再生成clip数・費用
- Git・必要なSSOT更新状況
- Fable受入結果

修正完了後も記事BのStatusは `USER_LISTENING_PENDING` のままとし、ユーザーの最終試聴PASSを待ってください。
```

## 2. 前提(調査結果、`docs/pm/RESULT_PACKET_KPGV.md`・OPEN-460)
- 対象: `er019_output/family_x_audio_production_wiring_01/tesla_spacex_merger_talks__run_nws_01/a2/` の `key_phrases.1.japanese_meaning`(`meaning_1.wav`、sha `eadb263e…`、F0 124Hz)。設定はAoede/gemini-3.8-flash-lite-tts で仕様どおり、TTS側が低音域の声を返したのが原因。同runのAoede音声はF0 170〜193Hz(参考)。
- ページ: `user_test/tesla_spacex_merger_talks_e2e_01/`(`er019_nws_final_page_01.py`が通し音声を`timeline.json`の秒数で切り出し)。Pages URL https://shimomura055.github.io/eigo-radio/user_test/tesla_spacex_merger_talks_e2e_01/index.html
- Advanced側はこの日本語clipを使っていない(英語KP clipのみStore再利用)。Advancedは変更しない。

## 3. 作業
1. **直列化**: 開始前に`Get-Process python`のcommand lineとACTIVE_TASKのASR-HOMOPHONE行で、別agentの有料run(X/Z runtime evidence)が走っていないことを確認。走っていれば終了まで待機(5分間隔・最大30分)。Master Audio Storeのmanifestは非atomic。
2. **再生成(1本のみ)**: 既存のProduction経路で該当clipだけを再生成する(X runnerのsegment/clip単位の再生成オプション、または既存のTTS retry経路。**人工entry・Gate迂回・Lockファイル直接編集は禁止**。該当する正規手段が無ければ、runnerの既存関数を使った最小のclip再生成scriptをDEV用に書き、それがProduction経路と同一のTTS設定[voice=Aoede、model、style_profile、speech_metadata]を使うことを設定dumpで証明する)。旧wavは削除せずSTALE退避(`meaning_1_STALE_<sha8>.wav`等)。Storeに旧clipが登録されていれば、新clipで置換ではなく新規entry+旧entryの参照を切る(既存の仕組みに従う)。
3. **Voice確認(参考指標、合否基準にしない)**: 新clipのF0を同runの他のAoede日本語clip(`meaning_2` 187Hz・`meaning_3` 174Hz等)と比較し、同程度かを報告。明らかに低音域(前回同様)のままなら、既存のTTS再試行上限内で再生成(上限・費用を報告)。上限内で改善しない場合は中止して報告(ユーザー判断)。**170Hz等の閾値をコード・SSOTに固定しない。**
4. **ASR QA**: 既存の日本語ASR検査(Production既定)で合格を確認(EXACT/NORMALIZED等の結果を記録)。
5. **差替え・組立・ページ**: `tts_generation_results.json`等の記録を新clipに更新(履歴を残す)、Standardの通し音声を既存のassemble経路で再構築(Advancedは触らない)、`timeline.json`更新、`er019_nws_final_page_01.py`でページ再生成(**Advanced側のmp3が不変であること**をsha比較で確認)。
6. **公開確認**: commit/push後、HTTP 200と公開側のPlaywright実再生(`er019_nws_play_verify_01.py`、全audio)、該当mp3(std_09相当)の日本語部分F0を参考記録。
7. **費用**: 出典付き(raw_usage_log)。見込み≈0.3〜1円。
8. **SSOT**: OPEN-460を`FIXED_INDIVIDUAL_CLOSED(個別修正でClose、包括対策は起票しない)`へ、OPEN-457の記事B行に「KP1日本語clip差替え済み・USER_LISTENING_PENDING維持」を追記、DECISION_LOG 1エントリ(ユーザー決定A案のみ・原文所在)、USER_DECISION_REGISTER(本件判断済み。**包括対策の新規判断項目は起票しない**)、REPORT_LEDGER 1行。commitは明示add(`-A`禁止)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- 他clip・本文・Advancedの変更、新Gate設計/Trial/実装、閾値の固定、再試行上限超過、Store manifestの手編集、別agent run中の有料呼出。

## 5. 報告(docs/pm/RESULT_PACKET_KPGVF.md、同内容を最終報告で)
(1)修正前後のVoice確認(F0参考値、生成設定dump) (2)ASR・QA結果 (3)更新後の試聴URL+公開再生検証 (4)再生成clip数・試行回数・費用(出典) (5)Advanced不変の証拠(sha) (6)commit・raw URL・SSOT (7)残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。