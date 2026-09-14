# USER-TEST-AUDIO-COMPLETION-01 — ユーザー実試聴用音声完成 最終REPORT

管理ID: `USER-TEST-AUDIO-COMPLETION-01`(Sonnet複数回委任、統合: `PM-CLOSEOUT-CONSOLIDATION-133`)
日付: 2026-09-14
性質: Family C / Trend / Discovery / Voicesの4対象について、ユーザーが実際にWebブラウザで試聴できる状態(GitHub上の実音声ファイル・相対パスplayer・`file:///`不使用)まで進めた。Production採用(`PRODUCTION_WIRED`)ではない。

---

## 1. Family C / Home robots

- Status: Trial-09は引き続き`VALIDATED`(仕様変更・音声/テキスト再生成なし)。
- 問題: WAVがGitHubに未収録だった原因は、未addではなく`.gitignore`の`*.wav`ルールによる除外だった。
- 対応: mp3化(完成episode+segment38件、追加費用¥0)、player.htmlの参照を相対パスへ修正。
- Web player URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/player.html`
- 直接音声URL: `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/web/family_c_home_robots_trial_09.mp3`
- Playback確認(HTTPレベル): 直接音声=HEAD 200・Content-Type audio/mpeg・Content-Length 2,717,904bytesが実ファイルと一致。player=GET 200・text/html(raw.githack.comはHEAD非対応)。player内の相対参照(episode+segment3件)をraw.githubusercontent.com基準で解決しHEAD 200を確認。実際にブラウザで聴く確認はユーザー側で実施してください。
- 追加費用: ¥0(API呼び出しなし)。

## 2. Trend

- A2 player URL: **未生成**。`point_two`(「Alexa+」のASR双方向表記揺れ)が読み整形後も解消せず、既存Production安全装置`ER-011-HUMAN-REVIEW-COST-GUARD-01`によりHUMAN_REVIEW_LOCKEDへ遷移したためSTOP。
- B1 player URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/player.html`
- Audio Validation結果(B1): gate_off=PASS、gate_on(`verify_episode_audio_validation_gate`)=PASS。緩和・overrideなし。
- 完成episode duration(B1): 364.734秒。
- 追加音声化費: ¥160.15(A2の未完成分実費を含む)。
- 最終Production 1生成セット総原価: **¥334.18**(本文¥174.03+音声化¥160.15)。

## 3. Discovery

- 人手選定したB1 Key Phrase 5件: nothing to do but think / reduced the feeling of connection / being in the present moment / actively choosing solitude / complicates any simple cultural story
- 「have agency」を外した理由: 語彙動詞用法の"have"が、既存Key Phrase選定Validatorの有限助動詞ブロックリストに誤って一致し、自動選定が4回連続`KEY_WORDS_STRUCTURE_INVALID`となったため。Validator自体は本タスクでは無変更(Production QA変更のためユーザー判断待ち)。
- Validator問題Open Item ID: **OPEN-152**
- A2 player URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html`
- B1 player URL: **未生成**。`full_story_part2`の長文1文(「In a study of 2,557 college students…」)がTTSから3回とも脱落し、数字読み整形後も再発したためHUMAN_REVIEW_LOCKEDでSTOP。
- Audio Validation結果(A2): gate_off=PASS、gate_on=PASS。B1: 未実行(Assembly未到達)。
- 完成episode duration(A2): 480.082秒。
- 最終総原価: **¥565.10**(本文¥463.27+音声化¥85.51+¥16.32、Key Phrase B1B人手選定のLLM2呼び出しは推定¥1〜6・ログ未記録)。

## 4. Voices

- 2V player URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v/player.html`
- Audio Validation結果: **PASS**(14 segment全てVALIDATED、緩和・overrideなし)。
- Comment・Fact Safetyが実際にepisodeへ反映された証拠: `comment_fact_safety_evidence.json`にComment Contract節(新テキスト全文・support_status全OK・deviation_overall_status=LEDGER_COMPLIANT・episode内タイムライン開始秒[comment_1=94.466s/comment_2=131.309s/comment_3=227.247s/comment_4=273.229s])を記録。comment_2は旧文(挿入句を含む文構造)から新文(挿入句を含まない構造)へ差し替え、1attempt目でASR完全一致(NORMALIZED_MATCH)。
- 残存Leakageの記録: `comment_fact_safety_evidence.json`の`analytical_leakage_check_residual_flag`節にvoice_b(5項目)・tension(2項目)を原文引用込みで記録。player.html本文にも同じ限界を明記し、試聴対象から隠していない。
- Status: **PARTIAL / USER TEST READY**(`PRODUCTION_WIRED`未承認、OPEN-151のStatusは本タスクでは変更していない)。
- 完成episode duration: 309.485秒。
- 最終総原価: **¥185.74**(¥140.39+¥32.34+¥13.01)。

---

## 5. 未完成2件(Trend A2・Discovery B1B)の扱い

| 項目 | Trend A2 | Discovery B1B |
|---|---|---|
| 症状 | `point_two`の「Alexa+」がASRで双方向に表記揺れ | `full_story_part2`の長文1文がTTSから3回とも脱落 |
| 実施済み対応 | Markdownリンク除去・Alexa+→Alexa Plus等の読み整形 | 算用数字の読み整形(30→thirtyなど、誤読は解消) |
| 結果 | 読み整形後も新canonicalで1attempt目にASR_VALIDATION_UNCERTAIN、既存Human Review Cost Guardで自動ロック | 数字誤読は解消したが、複雑な修飾句を伴う1文が新canonicalでも3attempt全てで脱落、既存retry上限(3回)で未解決 |
| 現在の状態 | HUMAN_REVIEW_LOCKED(`approve_regenerate()`未使用) | HUMAN_REVIEW_LOCKED(`approve_regenerate()`未使用) |
| ユーザー判断の選択肢 | (a)`approve_regenerate()`実行を承認する、(b)「Alexa+」表記の辞書拡張等の恒久対応を検討する、(c)別対応 | (a)該当文をさらに言い換える読み整形(意味不変、要承認)、(b)segment分割等の構造変更を承認する、(c)`approve_regenerate()`実行を承認する、(d)別対応 |

## 6. Human Review Lockの扱い(Fable判断、DECISION_LOGに記録)

全タスクを通じて`approve_regenerate()`(ユーザー明示指示専用、対話的操作限定)は一度も使用していない。読み整形・部分再生成後のテキストはcanonical_text_sha256が旧lockエントリと異なるため、`er011_human_review_lock_01.py`の既存仕様(「canonical_text changed since last lock; treated as new version」)により通常のAUTO_PROCESSING(初回生成)として扱われた。旧lockエントリはすべて無編集のまま残存している。承認代行は行っていない。

## 7. 新規Open Item登録

- **OPEN-152**: Key Phrase選定Validatorが語彙動詞have/has(例: "have agency")を有限助動詞ブロックリストで誤検知する。Discovery B1Bで4回失敗・人手選定で回避。`USER_DECISION_REQUIRED`、優先度MEDIUM。
- **OPEN-153**: 音声化経路のTTS入力前処理・TTS読み飛ばし系gapの集約(サブ項目a〜g: Markdownリンク/記号/ハイフン複合語の読み整形未実装、算用数字読み整形未実装、長文1文丸ごと読み飛ばし、Comment挿入句の読み飛ばし、ブランド名表記の双方向ASR揺れ、Key Phrase音声未配線、Key Phrase音声ステータス記録バグ)。Trend A2・Discovery B1Bの完成を直接阻害しているためBlocking、優先度HIGH。`USER_DECISION_REQUIRED`。

---

## 8. 費用表(PM_GOVERNANCE 15-8形式)

| Family | 本文総原価 | 音声化差分 | 最終総原価 |
|---|---|---|---|
| Family C Trial-09 | ¥96.30(既報、参考・別予算枠) | ¥0(mp3化・player修正のみ、API呼び出しなし) | ¥96.30(不変) |
| Trend | ¥174.03 | ¥160.15(B1B完成分+A2未完成分の実費) | ¥334.18 |
| Discovery | ¥463.27 | ¥85.51+¥16.32(A2完成分+B1B未完成分の実費) | ¥565.10 |
| Voices(2V) | ¥140.39 | ¥32.34+¥13.01(run1+comment_2再生成CONT1) | ¥185.74 |

本タスク(`PM-CLOSEOUT-CONSOLIDATION-133`、Git記録・Web到達確認・SSOT反映)自体の費用: ¥0(API呼び出しなし)。

## 9. Web到達確認結果(GitHub push後、HTTP取得)

直接音声4件(raw.githubusercontent.com、HEAD)はいずれも初回でHTTP 200・Content-Type: audio/mpeg・Content-Lengthが実ファイルサイズと一致。player4件(raw.githack.com)はHEADメソッド非対応(403 Forbidden)のためGETで確認し、いずれも初回でHTTP 200・Content-Type: text/html。各player.html内の相対パス(`src=`)を同じbase URLで解決し、完成episodeと先頭segment3件のHEADが200であることを確認した(Trend A2・Discovery B1Bはplayer/mp3とも未生成のため対象外)。CDN反映遅延による404は発生せず、再試行は不要だった。詳細: `docs/pm/web_playback_check_UT01.json`。

全4 player.htmlとも、`src=`/`href=`属性に`file:///`・絶対Windowsパス(`C:\`)は0件(機械確認済み)。

---

## 10. ユーザーが今クリックして試聴すべきURL(4件)

1. Family C / Home robots: `https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/player.html`
2. Trend B1: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/player.html`
3. Discovery A2: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html`
4. Voices 2V: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v/player.html`

(Trend A2・Discovery B1Bはロック中のため未生成。上記4件のみが現時点で試聴可能。)
