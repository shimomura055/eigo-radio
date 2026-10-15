<!-- sha256=55365a1893543c6d432685901c81b6b20b0418e5cacd60be03494142c223207a chars=9237 source=agent-aadd9d0e78b531cf3.jsonl (逐語、抽出のみ) -->
# Opus独立技術レビュー(11-3 条件C): U1是正・U2整理・B-A2-01 narrator計画
管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` / read-only / 費用JPY0 / Production採用判断はしていない

## 総評
方針(U1是正、U2は(i)維持＋記述訂正、B-A2-01の実音声取得)には同意する。ただし計画どおりの「`er078_asr_unified_judge_01.py:65`をFalseにする1行変更」をそのまま出すことには**条件付き同意**とする。計画書の誤受理評価(frozen 0/25)では検出できない経路が2つあるため。
(1) 登録読み辞書(`expected_readings`)が保護している語が素通りする経路(BLOCKER)。
(2) A5で新たにSecondaryへ回る「壊れた音声」が、Secondaryの空転写を経て技術STOPへ流れる経路(MAJOR)。
どちらも小さな修正で塞げる。A3(length)維持の根拠記述も事実と合っていない(MAJOR)。

---

## Q1 誤受理経路 → 条件付き同意(現行実装のままでは不十分)
- **Secondary受理基準の事実**: `_secondary_accept` は `classify_ja_asr_match(canon, stext, expected_readings, allow_reading_resolver=False)` が EXACT/NORMALIZED のときだけ受理する(`er007_ja_secondary_asr_01.py:604-608`)。EXACT/NORMALIZED の判定は**表層比較で、読み辞書チェック(protected_check_ja)より前**に行われる(`er007_ja_asr_validator_01.py:349-359`)。NORMALIZED は英字を小文字化する(`:122`)。つまりSecondaryの転写が原稿の表記をそのまま返した場合、その語の「読み」は一切検証されない。
- **経路A(BLOCKER, U1R-01)`reading_dictionary_mismatch`**: この信号は、PrimaryがひらがなやカタカナでTTSの誤読を具体的に示したときに立つ(`validator:290-305`)。例は2つ。
  - 登録語「Meta=メタ」をTTSが「エム・イー・ティー・エー」と読む。Primaryは「エムイーティーエー」(辞書不一致)、Azureは「META」を返し、小文字化でNORMALIZED一致になる。
  - 漢字の固有名詞で、TTSが辞書候補外の誤読をする。Azureは漢字表記を返してEXACTになる。
  どちらも結果は `PASS_WITH_WARNING` になる。これは「Meta vs メタン」の無条件PASSを塞いだ既存保護(validator:210-214、Phase 3b)の再発で、C2(`judge.py:115`「Azureが原稿の漢字表記と一致しても読み違いを区別できない」)と同じ構造の穴である。漢字側の多くは辞書候補に入るのでC2(A4)が先に拾うが、Latin・頭字語の登録語はC2では拾えない(`_scg_heterophone_candidate`は漢字読みの候補判定、`er007…:173-185`)。読みでの受理(PHONETIC_MATCH)は2026-10-11の安全条件で禁止されているため(`DECISION_LOG.md:20574`)、この経路でSecondaryが「原稿を正当に支持」できる手段はない。
  - **推奨**: A6のうち `reading_dictionary_mismatch` だけは除外として残す。名目はC1ではなく「登録読み保護(C2と同じ理由)」とする。entity_like と、辞書未登録の latin_in_canonical_diff は解放してよい(Azureのカタカナ出力は読みを表し、辞書未登録のLatin語には登録読みという基準自体がない)。A-3の「既存日本語ASR Validator・Pronunciation Ledgerとの整合確認」と「正当に支持すれば」の範囲内の実装判断と評価する。代替案は「Secondaryは呼ぶが、辞書不一致の語は表層一致を受理しない」だが、結果は常にNGになり費用だけが増えるので劣る。
- **経路B(MAJOR, U1R-02)空転写**: Azureが正常に完了して空文字を返すと(`er007…:278`)、`SecondaryOutcome.ok=False` になる(`judge.py:181`)。結果は `NG_SECONDARY_UNAVAILABLE`(`judge.py:431-448`)で、連続失敗カウントが進み(EN/JA共有の `_RUN_STATE`、`er007…:429-435`)、最終slotでは**HR Lockに行かず技術STOPになる**(`er007…:682-688`)。A5(類似度<0.4)で新たに流れ込むのは、無音・雑音・言語違いなど空転写を起こしやすい層である。このため現行の「NG_EXCLUDED→再生成→最終HR」が「技術STOP／circuit breakerでrun全体のSecondaryが停止」に悪化しうる。
  - **推奨**: JA adapterの `_secondary_fn` で「エラーなし完了の空転写」を `SecondaryOutcome(text=<no_speech sentinel>, accepted=False, label="NO_SPEECH")` として返し、`NG_BOTH` にする。JAに限定でき、EN挙動は変わらない。A-2 #5「両方NG→再生成」に合わせる実装修正である。
- **経路C(MINOR〜要観察, U1R-03)言語違い・アクセント**: Hangul転写(類似度0.0)は「Primaryの言語誤判定」か「TTSが日本語を正しく発話していない」かのどちらか。後者でも ja-JP固定のAzureは日本語へ寄せて原稿どおり返しうる。内容は正しいが音声品質の問題で、事後試聴でしか拾えない。(e-2)のMelos title wavで必ず切り分けること(下記Q7参照)。
- 類似度<0.4・カタカナentity_likeの通常ケース(g7・g8型)については、原稿全文の表層一致は偶然には起きにくく、値ガード・否定ガードもSecondary転写へ再適用される(`judge.py:456-460`)。解放は妥当。

## Q2 A3/A4/P1の線引き → A4・P1は同意、A3は根拠記述に不同意
- **P1**: Secondaryの前で `NG_PROTECTED` を返す(`judge.py:385-394`)。A-2 #7「数値・否定」と一致する。
- **A4(C2)**: 維持に同意。A-2 #2の「原則」とA-2 #7の「など」の範囲内で、2026-10-11にユーザーが逐語で採用した保護である(DECISION_LOG:20574)。Azureの漢字一致は「正当な支持」にならないので、A-2太字の「正当なPASSを拒否しない」とも矛盾しない。優先関係の整理は不要。
- **A3(MAJOR, U1R-04)**: 計画書は「独立音声品質QA」としているが、事実ではない。`length_ok` は**Primary転写の文字数**から計算されている(`er003_v1_crosslevel_audio_02_common.py:348`、`er003_v1_n3_01_tts_generate.py:725,734`、`er003_v1_sing01_news_tail_fix.py:192` ほか)。最終ANDもPrimary由来のままである。由来もC1と同じで、Opus推奨6をFableが採用したもの(ユーザーの逐語要旨20574には含まれない)。A-3の「固有名詞差・類似度0.4未満**等**」に入りうる。またA3はENにも効く(langs en,ja)。
  - **推奨**: 今回のU1解放には含めず、別の小委任で是正する。内容は「Secondaryが受理したら、Secondary転写でlengthを再評価する」で、複数の呼出元のAND修正になる。あわせてOPEN起票と、保存データのA3件数集計(API0)を行う。黙って恒久的に維持するのは不可(Q7)。

## Q3 Regression → 条件付き同意(負例の追加が必須)
- frozen 25行のうち、解放されるクラス(C1/A5)に当たるのは g7・g8 の**正例2行だけ**である。C群5行は否定や一般語で、解放クラスの負例ではない。したがって「誤受理0」は解放リスクについて何も検証していない(MAJOR, U1R-05)。
- **追加必須**:
  - (a) unit負例: 辞書登録Latin語(Meta=メタ)で、Primaryが「エムイーティーエー」、mockのAzureが「META」→NG。漢字の登録語でAzureが原稿表記→NG(U1R-01の固定)。空転写→NG_BOTHで技術STOPにならない(U1R-02)。EN側でA5/A6が無効のままであること。
  - (b) **live負例対照**: 誤った文面(例: 原稿「ガス」に対し「カス」、「Meta」に対し綴り読み、短語の別語)をTTSで生成し、正しい原稿に対して判定させる。6〜8clip、約JPY2〜3。期待値は全件NG。Azureが原稿側へ寄せるリスクを直接測れる唯一の手段である。
  - (c) (e-2)の集計に「NG_EXCLUDED→NG_SECONDARY_UNAVAILABLE」の遷移件数を加える(0であること)。
- 省略可: (e-3)のfresh正例は(b)を実施すれば任意でよい。α/βの分け方は妥当。反転したtestとは別に、`U1=True` をmonkeypatchしたロールバックtestを1本残すこと。

## Q4 U2 → (i)維持に同意。SSOT訂正の範囲を拡げること
- `force_secondary=True` の実体は `common.py:364` の1箇所で、利用先はA2 segmentのfallback・A2 LR再TTS・X/ZのA2 topic_intro(`er019:1259`、`er063:669`)・Family B A2見出し(`a2prod:740-743`→`n3 generate_a2_segment_with_slowdown`)である。B1や他の経路への拡大はない。
- **見落とし(MINOR, U1R-06)**: `er003_v1_sing01_news_tail_fix.py:178` の技術失敗時のminimal fallbackは `force_secondary` を渡していない(`:206-211`)。これはA2/B1共通の広帯域ナレーション(Family B A2のHook/Tension/Closing、ZのB1 narrator `er063:637-641`)で使われる。2026-08-26の決定は2箇所限定なので(DECISION_LOG_HISTORY:4922-4930)違反ではない。ただし `CURRENT_SPEC.md:1933` の「fallback経由英語音声はSecondary必須」はA2の中でも実態より広い。SSOT訂正では対象を「`_run_a2_minimal_fallback_attempt`経由のみ」と明記し、news_tail_fix系は対象外とOPEN候補に記録する(拡大はA-4太字によりしない)。既存のOPEN-274(LR再TTSがminimal fallbackに依存)と関連付けること。
- 死んだ定数(`U2_FORCE_SECONDARY_SCOPE`)は削除してよい。代わりに `force_secondary=True` の呼出点が1箇所であることを静的testで固定し、根拠のない拡大を機械的に防ぐ。KP側の撤去(`8503226c2`)は本レビューでは未照合(Grepで現存0件は確認済み)。

## Q5 narrator harnessの同等条件 → 条件付き同意。ただし代替案を推奨
- 内側のラッパーを直接呼ぶ方式では、検証したい「Family B入口」(呼出引数・前処理)を手で再現することになる。**推奨は `run_tts_a2_2v_new_topic`(`er012_b_family_production_runner_01.py:1705-1757`)を、実在する新規topicのparts.jsonでそのまま呼ぶこと**。追加費用はtopic_introとVoice A/B本文の3〜5clip分(+JPY2〜4程度)で、共有narrationはMaster Storeから再利用される。
- 直接呼び出しを採る場合の必須条件は以下。
  - (a) `@secondary_run_scope.with_secondary_run` 相当でrun単位のcacheとcircuit breakerを張る。
  - (b) 前処理を一致させる。見出しは `tts_safe_number_words_en(tts_safe_en())`、本文は `tts_safe_news_en()`。`sc.assert_no_point_number_label` と `cl.segment_context(name)` も通す。
  - (c) 出力パスを `…/<theme>/a2/narration/<name>.wav` のレイアウトにする。`review_lock._has_valid_narration_layout`/`derive_segment_key` が成立しないと、segment_id・role gate・HR Lockが本番と別の挙動になる。
  - (d) flagやmoduleをmonkeypatchしない。`tts_backend` も渡さない(本番は既定値)。
  - (e) attempt_history/HR Lockは共有ファイルに書かれるので、実行前後の差分を記録し、隔離パス由来のsegment_keyであることを確認する。
  - (f) 「tts_generation_results.jsonへの記録」と「試聴リスト導出」はrunner側の処理なので、leafだけを呼ぶ方式ではこの2項目は未検証になる。runnerの書込・導出関数を同じように呼ぶか、検証範囲外と明記する。

## Q6 X-B1-06を区分3とする分類 → 不同意(MINOR, U1R-07)
- 経路は `ensure_key_phrase_english_component`(Master Store)を通る(CSV行7)。新規記事のKP phraseは通常Store missになり、leafで新規生成される。区分3(再利用・複製)が当てはまるのはhitのときだけ。正確には「3と2の混在(miss側は同じleafが他の入口で実音声検証済み)」である。
- **推奨**: 約JPY0.7でX B1入口からStore missを確実に起こす新規phraseを1本生成し、区分1へ上げる(bnarrと並列で実施可)。あわせて、CSVのX-B1-06行に残る「R(3回へ揃える)」とCURRENT_SPEC:2685の「KP英語phrase=4回」の記述の食い違いを訂正すること。

## Q7 新たな USER_DECISION_REQUIRED
**現時点では新たなユーザー判断は生じていない**。ただし条件が3つある。
1. U1R-01(登録読み保護を残すこと)は、A-3自身の「正当に支持」「Validator整合」とC2の前例の範囲内でFableが判断してよい。ただし「固有名詞差のうち登録読み不一致だけはSecondaryの表層一致を受理しない」ことは、ユーザー報告に**明示**すること(黙って範囲を狭めない)。
2. A3を是正せず恒久的に維持するなら、A-2太字と衝突するためユーザー確認が必要になる。是正を計画するならFableの判断でよい。
3. (e-2)でMelos titleが「TTSの言語違い音声なのにAzureが原稿どおり返してPASS」と判明した場合、言語判定QAの追加は新しい仕様なので、その時点で `USER_DECISION_REQUIRED` になる。

---

## 指摘一覧
| ID | 重大度 | 内容 |
|---|---|---|
| U1R-01 | BLOCKER(計画どおりのまま出す場合) | `reading_dictionary_mismatch` をSecondaryへ回すと、表層EXACT/NORMALIZEDで登録読みの誤りが素通りする。A6のうちこれだけは除外として残す(登録読み保護)。負例testで固定する |
| U1R-02 | MAJOR | Azureの空転写(正常完了)が `NG_SECONDARY_UNAVAILABLE` になり、最終slotで技術STOP、さらにcircuit breakerへ進む。A5解放で増える。JA adapterでNG_BOTH化する |
| U1R-03 | MINOR(条件付きで昇格) | Hangulなど言語違いの音声をAzure ja-JPが原稿へ寄せて受理する懸念。(e-2)で切り分ける |
| U1R-04 | MAJOR | A3(length_ok)はPrimary転写の文字数由来で、独立QAではない。根拠記述を訂正し、別委任で是正しOPEN化する |
| U1R-05 | MAJOR | Regressionに解放クラスの負例がない。unit負例とlive負例対照(誤文面TTS、約JPY2〜3)を追加する |
| U1R-06 | MINOR | news_tail_fix:178 のminimal fallbackに force_secondary がない(A2/B1共通)。CURRENT_SPEC:1933/2685 の訂正範囲に含め、OPEN候補とする(拡大はしない)。force_secondary呼出点の静的testを置く |
| U1R-07 | MINOR | X-B1-06は3と2の混在。JPY0.7で1本追加して区分1へ。CSVの3回/4回の記述矛盾も訂正 |
| U1R-08 | MINOR | narrator harnessは `run_tts_a2_2v_new_topic` を呼ぶ方式を推奨。直接呼ぶ場合はQ5の(a)〜(f)が必須 |
| U1R-09 | MINOR | `_scg_exclusion_reason`(診断用)はC1をC2より先に判定するため、解放後にA4で除外されたclipの表示理由が「C1」になりうる。コメント(judge:64-66,116-117、er007:84,394)も更新する |
| U1R-10 | MINOR | 既存の失敗2件(koro系、ORTHOGRAPHIC_VARIANT_CONFIRMED)はJAの受理集合(OF-AUW-08)に関わる。「新規失敗0」の基準を確定する前に、main側の状態を切り分けておく |

## 確認した証拠(file:line)
- `er078_asr_unified_judge_01.py`: 64-66, 111-140, 172-199, 336-348, 379-399, 431-487
- `er007_ja_secondary_asr_01.py`: 83-84, 173-215, 218-278, 429-459, 535-616, 625-688
- `er007_ja_asr_validator_01.py`: 95-124, 202-239, 285-330, 349-359, 397-504
- `er003_v1_n3_01_tts_generate.py`: 716-734
- `er003_v1_crosslevel_audio_02_common.py`: 348, 364(Grepで確認)
- `er003_v1_sing01_news_tail_fix.py`: 175-211
- `er012_b_family_production_runner_01.py`: 1705-1757
- `er012_b_family_voices_a2_production_01.py`: 740-756
- `er063_family_z_audio_01.py`: 634-672
- `er019_family_x_audio_production_runner_01.py`: 1256-1264
- `CURRENT_SPEC.md`: 1933, 2016, 2685-2688
- `DECISION_LOG.md`: 20574, 20580
- `OPUS_REVIEW_A_01_VERBATIM.md`: 76-79
- `APPLICABILITY_MATRIX_01.csv`: 7
- `U1_U2_SECTION_PLAN_09.md`: 全文

未照合の項目: `git show 8503226c2`、`DECISION_LOG_HISTORY.md:4922-4930`、`er003_v1_sing01_audio_generate.py:118/158` がProduction経路かどうか(U1R-06の範囲確定のため、委任_10でGrep照合を推奨)。
