FABLE-DELEGATION-MARKER: FX-KP-JA-GLOSS-VOICE-MISMATCH-INVESTIGATION-01-委任_01-20261023

# 委任_01: Family X 記事B Standard の Key Phrase 日本語意味「定款」の再生Voice不一致 — 調査・原因特定のみ(API費用0・Production変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-JA-GLOSS-VOICE-MISMATCH-INVESTIGATION-01_委任_01.md`(N≈314〜324、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FX-KP-JA-GLOSS-VOICE-MISMATCH-INVESTIGATION-01_USER.md` に逐語保存。
3. `docs/pm/ACTIVE_TASK.md`: 別agent(ASR-HOMOPHONE 委任_04)が並行中。編集直前に再読込し、「並行タスク」として本管理IDの1行を追加するだけ(他行は触らない)。

## 1. ユーザー指示原文(逐語)
```
## Claude Codeへの指示:Key Phrase日本語意味のVoice確認

**対象:Family X「マスク氏の『良い考え』で、合併話が渋滞する?」Standard**

試聴ページ:
https://shimomura055.github.io/eigo-radio/user_test/tesla_spacex_merger_talks_e2e_01/index.html

### 確認事項

Key Phrase `articles of incorporation` の日本語意味「定款」について、本来は女性Voiceのはずが、試聴時に男性Voiceで再生されました。

**今回はこの1点だけ調査してください。**

1. 現行Production仕様で、この日本語意味に割り当てるべきVoiceを確認。
2. 実際に生成された音声のVoice設定(voice ID、モデル、生成ログ)を確認。
3. Voice設定ミスなのか、音声ファイルの取り違え・再利用・試聴ページ側の問題なのか、原因を特定。
4. 同じ不具合が量産時にも発生し得る構造的問題かを確認。

### 作業範囲

- **調査・原因特定のみ。**
- 現時点では音声再生成・コード修正・Production変更は行わない。
- API費用を発生させず、既存ログ・設定・音声ファイルから調査する。
- Fableによる確認を含め、原因と必要最小限の是正案を簡潔に報告。

ほかの記事・音声の調査には拡大しないでください。
```

## 2. 既知情報(Fable)
- 記事B: slug `tesla_spacex_merger_talks`、音声run dir `er019_output/family_x_audio_production_wiring_01/tesla_spacex_merger_talks__run_nws_01/`(a2=Standard)、試聴ページ生成script `er019_nws_final_page_01.py`、ページ `user_test/tesla_spacex_merger_talks_e2e_01/`。Standard KP: articles of incorporation / vote as a separate group / under review。Advanced KPにも `articles of incorporation` が含まれ、**Adv KP2はStd音声をMaster Audio Storeから再利用**した記録がある(`docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md`)。再利用・取り違えの線を特に確認すること。
- Family X StandardのVoiceはAoede単独、AdvancedはAoede+Charon(男性的)。KPの日本語意味(gloss)clipのVoice仕様はCURRENT_SPEC(「Key Phrase」「gloss」「日本語」「Voice」でGrep)と、scaffold/TTS側の実装(`er003_v1_n3_01_scaffold_generate.py`、`er019_family_x_audio_production_runner_01.py`、`er006_master_audio_store_01.py`の等価key、KP再利用`er104_kp_vote_reuse_01.py`)で確認。

## 3. 調査手順(読取のみ)
1. **仕様**: 現行Productionで、Standard KPの日本語意味clipに割り当てるべきVoice(仕様行・実装行を引用)。Advanced側の同clipのVoice仕様も併記(Charonになり得るか)。
2. **実態**: 該当clipの生成記録(tts_generation_results / manifest / raw_usage_log / speech_metadata)から voice ID・モデル・生成時刻・source(新規生成 or Store再利用 or stored_evidence_rejudged)・wav path・sha256 を特定。Std側とAdv側の両方の「定款」clipを比較(sha一致なら同一ファイル)。
3. **ページ側**: `user_test/tesla_spacex_merger_talks_e2e_01/` のStandardページが参照するmp3/wavがStd run dirのどのclipに対応するかを確認(ページ生成scriptのマッピング、ファイルsha)。Std playerにAdvのclipが混入していないか。
4. **聴取確認(Fable判断用の補助、API 0)**: 当該clipの基本周波数(F0)等の既存指標script(例 FZVS trialで使ったF0算出)で、Aoede(女性的)とCharon(男性的)のどちらに近いかを機械的に確認。推測で断定せず「指標上は〜」と表現。
5. **原因の分類**: (a)Voice設定ミス(仕様どおりでない設定が渡った) / (b)Store再利用・等価keyにVoiceが含まれない等で別Voiceのclipが再利用された / (c)ページ生成側のファイルマッピング誤り / (d)仕様自体がStdでも男性Voiceを許容 / (e)その他。事実と推測を分ける。
6. **構造性**: 量産時に再発し得るか(再利用key・ページ生成・scaffoldの経路から判断)。該当するなら影響し得る範囲(どの経路・どの条件)を特定。**他記事の全数調査はしない**(経路の確認に必要な最小限のコード・設定読取に留める)。
7. **必要最小限の是正案**: 原因別に1〜2案(例: 等価keyにvoiceを含める/ページmappingの修正/該当clip1本の再生成約0.3円)。実施はしない。

## 4. 禁止
- API呼出、音声再生成、コード修正、Production/SSOT仕様変更、他記事・他音声への調査拡大。

## 5. 報告(docs/pm/RESULT_PACKET_KPGV.md、同内容を最終報告で; SSOTはOPEN_ITEMSに調査結果を1 item起票[Status=INVESTIGATED_PENDING_USER]、REPORT_LEDGER 1行、commit/push・secret_scan hits=0)
(1)結論(原因分類と確度) (2)仕様上あるべきVoice(出典) (3)実際のVoice設定・生成ログ(voice ID/モデル/source/sha) (4)ページ側のマッピング確認 (5)F0等の機械指標 (6)構造的問題か・影響範囲 (7)必要最小限の是正案と費用 (8)commit・raw URL + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。