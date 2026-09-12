# FAMILY-A-TREND-AI-MANUFACTURING-A2-JA-FOREIGN-TOKEN-GATE-RECONCILE-01

管理ID: FAMILY-A-TREND-AI-MANUFACTURING-A2-JA-FOREIGN-TOKEN-GATE-RECONCILE-01
種別: read-only調査+設計案(Git操作なし・API呼び出しなし・Production/辞書/Ledger/SSOT変更なし)
対象事象: `FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01_REPORT.md`のA2で、
ER-009 Japanese Foreign Token Gateが未登録token「AI」を検知しjapanese_title・preview・
comment_1〜4・kp5日本語gloss(meaning_5)の計7segmentがHUMAN_REVIEW(STOPPED)。

## 1. 既存仕様のreconcile

### 1-1. ER-009 Japanese Foreign Token Gateの仕様

実装: `er003_audio_tts_asr_safety.py::classify_foreign_tokens_in_japanese_text()`
(行681-769)。日本語canonical text中のLatin文字トークンを4分類する
(rule-based、新規LLM呼び出しなし):

1. `NEEDS_JAPANESE_PARAPHRASE` — 制作内部ラベル(`Part 1`/`Point Two`等、
   `_INTERNAL_LABEL_WORDS = ("Part","Point","Comment","Section","Step","Chapter")`
   + 数字/ローマ数字/英単語序数のみを検出する専用正規表現)
2. `READING_DICTIONARY` — `DEFAULT_JA_READING_DICTIONARY`(行681-684、
   ハードコードされた7エントリのみ: `cm/kg/km/kcal/ceo/wi-fi/cafe`)に
   登録済みのトークン
3. `ENGLISH_PRONUNCIATION` — 呼び出し側が渡した`known_key_phrase_terms`
   (その記事のKey Phrase英語表現`used_form`)がcanonical text中に
   **文字列としてそのまま含まれる**箇所
4. `HUMAN_REVIEW` — 上記いずれにも該当しない残りのLatin文字トークン

TTS呼び出し自体をブロックするのはカテゴリ4のみ(過検知でProduction全体を
止めないための既定設計、ER-009-JA-FOREIGN-TOKEN-GATE-01決定事項)。

### 1-2. 読み辞書への登録経路

`DEFAULT_JA_READING_DICTIONARY`は`er003_audio_tts_asr_safety.py`内の
**リテラルなPython dict**であり、専用の登録関数・CLI・外部データファイルは
存在しない(コードベース全体をgrepしたが`reading_dictionary=`の呼び出し
引数以外にこの辞書へ書き込む仕組みは見つからなかった)。エントリを増やす
唯一の手順は、このProductionソースファイルを直接編集することであり、
実際に現在の7エントリはGate新設時(2026-08-26、ER-009-JA-FOREIGN-TOKEN-
GATE-01)に一度に追加されたのみで、以降の追加実績は無い(git blame相当の
追跡はしていないが、DECISION_LOG_HISTORY.md該当エントリに追加時の記述
以外に辞書拡張の決定エントリが見当たらない)。

なお`er006_output/pronunciation_ledger_01/ledger.json`(`er006_pronunciation_
ledger_01.py`)は**別の仕組み**であり、英語TTS/ASR retry cascadeが学習した
IPA/発音ヒントをハッシュキーで保存する、英語固有名詞の発音再試行支援用
レジストリである。ER-009 Gateの`DEFAULT_JA_READING_DICTIONARY`(日本語文中の
Latin文字トークン分類用)とは別物であり、混同しないよう明記する。

### 1-3. 過去の同種tokenの扱い

- コードベース全体・`er011_output/`配下の既存記事コーパス
  (`a2_support_texts.json`13件・`keywords_canonicalized.json`・`parts.json`)
  をGrepベースで走査したところ、大文字2〜5文字の英字トークンで
  日本語混じり文中に出現したのは、今回の「AI」(9件、2ファイル
  =`family_a_trend_ai_manufacturing_prod_run_01`のa2_support_texts.json+
  keywords_canonicalized.jsonのみ)だけであり、IoT/GPS/EV/CEO/GDP/DX/SNS/PC
  等の他の略語は既存コーパスの日本語segmentに一件も出現していなかった
  (「CEO」は辞書に登録済みだが、実コーパスでは日本語文中に出現した実例は
  今回の走査範囲では見つからなかった=当時何らかの理由で予防的に登録された
  可能性が高い)。
- 唯一の実運用HUMAN_REVIEW実例(`er009_output/ja_foreign_token_gate_01/
  human_review_queue.jsonl`)は、pool_n8_airport_lineのA2 comment_4
  「英語のIn One Lineで確認しましょう」中の`In`/`One`/`Line`(2026-08-28)。
  これは「AI」と異なり**トピック自体の内容語ではなく、番組構成上の
  内部セクション名(In One Line)を日本語文中で名指ししてしまった**ケースで
  あり、実際に現行Production版の該当comment_4を確認したところ
  「英語のまとめで確認しましょう」へ言い換え済みだった(辞書登録ではなく、
  台本側のparaphraseで解決)。すなわち過去の唯一の実インシデントは
  「言い換えで解決すべきラベル漏れ」型であり、今回の「AI」のような
  「記事の主題そのものである内容語」型の実インシデントは今回が初めて。

## 2. 原因切り分け

**主因は(i)辞書の網羅漏れ**。`DEFAULT_JA_READING_DICTIONARY`は2026-08-26の
Gate新設時に当時判明していた7語だけを reactive に登録した小規模辞書であり、
「AI」のような一般的な略語も含め、その後の新規追加実績が無い。今回
初めて「AIそのものがトピックである記事」を生成したため、初めてこの
網羅漏れが顕在化した。

**副因は(ii)Key Phrase経由の保護が個別segment単位でしか効かない設計**。
`known_key_phrase_terms`は、Key Phrase日本語gloss segment自身
(`kp{rank}_ja_charon`/`meaning_{i}`)を生成する呼び出しにのみ、その
Key Phrase自身の`used_form`を渡す設計になっている
(`er003_v1_n3_01_tts_generate.py`行775-777・893-895)。一方、
japanese_title/preview/comment_1〜4を生成する呼び出し(同ファイル行
824・831)には`known_key_phrase_terms`を一切渡していない。したがって、
仮に記事のKey Phrase used_formが「AI-run factories」であっても、その
「AI」という文字列がcomment文中に単独で出現した場合は保護対象外であり、
これは意図的な設計(「このKey Phraseは意図的に英語発話させる箇所」という
局所的な例外であり、「記事全体でこの単語は安全」という意味の一般化では
ない)であって、バグではない。

**(iii)Gate仕様が略語一般を想定していないという解釈は不正確**。Gateの
4分類設計自体は略語(READING_DICTIONARY)を明示的に扱う分類を持っており、
「略語一般を想定していない」のではなく「その略語辞書の中身が薄い」だけ
である。Gateの過検知抑制方針(カテゴリ1〜3以外はHUMAN_REVIEWへ)は、
2026-08-26時点でユーザー承認済みの意図した安全設計であり、これ自体は
今回の事象の原因ではない。

**A2とB1Bで挙動が異なった理由**: B1BのGateが「AIを正しく扱えた」わけ
ではなく、**そもそもGateの適用対象自体が異なる**。B1のPreview/Comment
1〜4は日本語ではなくeasy English(ER-009-JA-FOREIGN-TOKEN-GATE-01の
決定エントリに明記済み、「B1(b1_support_texts.json)は…B1 Comment/
Previewは日本語ではなくeasy Englishのため、そもそも対象外」)であるため、
Gate自体が発火しない。B1でGateが実際に通過するのはKey Phrase日本語gloss
(`kp{1-5}_ja_charon`)のみであり、今回の記事ではB1側のKey Phrase Selector
が独立に選定した5語(`not there yet`/`real production settings`/
`self-directed robot`/`money trail`/`data-center demand`)がたまたま
「AI」という文字列を含んでいなかった(実データで確認済み、
`b1b/key_phrases/keywords_canonicalized.json`)。つまりB1B完走は
「Gateが機能した結果」ではなく「Key Phrase選定の巡り合わせでAIという
語が登場しなかった」という偶然であり、次にB1でも「AI」を含むKey Phraseが
選ばれれば同じ現象(kp_ja_charonのHUMAN_REVIEW)がB1側でも起こり得る。

## 3. failure mode一般化(既存コーパスでの出現頻度)

`er011_output/`配下の`a2_support_texts.json`(13件)・`keywords_
canonicalized.json`・`parts.json`をGrepベースで走査し、日本語文字を含む
文字列中に出現する大文字2〜5文字のLatin文字トークンを集計した結果:

```
AI: 9 occurrences, files=2 (家族=family_a_trend_ai_manufacturing_prod_run_01のみ)
他の略語(IoT/GPS/EV/CEO/GDP/DX/SNS/PC等): 0 occurrences
```

**解釈**: 「日本語ナレーション中に未登録の英語略語が出現する」という
failure modeは、これまでの22件超のテーマでは一度も実発生しておらず
(コーパス内で唯一の実発生例が今回)、**一般的な略語漏れ問題ではなく
「AI」という1語(および将来同様にテーマの主題語になり得る少数の高頻度語)
に限定された、Trend/News editorial modeが技術トレンド系テーマを扱う際に
特有のリスク**と判定する。ただし今後のテーマ選定(ユーザーが選ぶ複数
候補提示ルール、`PM_GOVERNANCE.md`13節)でAI/IT関連の技術トレンドが
選ばれる可能性は高く、その場合は毎回同じ失敗が再現する確度が高い
(「AI」はテーマの主題語である限りほぼ全Japanese narrationに出現するため、
1記事あたり複数segmentが同時にSTOPPEDになる=今回同様7segment規模)。

## 4. 候補案(採用はユーザー判断、実装はしない)

| 案 | 内容 | 品質(Quality) | 費用(Cost) | 納期(Delivery) | 回帰リスク | ER-009設計思想への影響 |
|---|---|---|---|---|---|---|
| A(推奨) | `DEFAULT_JA_READING_DICTIONARY`へ`"ai": "エーアイ"`を追加登録(既存7エントリ追加時と同一の手順=Production該当行を直接編集)。必要なら同時にIT/EV/IoT/DX等の高頻度技術略語も予防的に追加するかは別途ユーザー判断 | 高(「エーアイ」は確立した一般的読みで既存のCEO→シーイーオーと同種、誤読リスクほぼ無し) | ¥0(コード編集のみ、LLM/TTS呼び出し無し) | 最速(1行追加+既存テストスイート再実行) | 極小(辞書へのadditiveな1エントリ追加のみ、他の分類ロジック・他テーマの挙動に影響しない。既存13件のGate単体テストは無変更で全PASS見込み、新規テストケース追加が望ましい) | 弱めない。HUMAN_REVIEWは「確信が持てないtoken」に対する最終防波堤のままであり、「AI」を確立した略語として辞書対応するのは既存7語と同じ運用の延長 |
| B | Gate側で「Key Phrase一致」の判定を、記事全体のKey Phrase used_formに含まれる**部分文字列**(トークン単位)にも拡張し、known_key_phrase_termsを全Japanese segment呼び出しへ配線し直す | 中(意図と異なる箇所で誤って英語発話許可が広がる可能性=false negative方向のリスクがA案より高い) | 中(コード変更範囲が`classify_foreign_tokens_in_japanese_text()`本体+全呼び出し箇所、新規テスト設計要) | 中(設計変更のレビュー・既存回帰確認に時間がかかる) | 中〜高(Gateの中核ロジック変更のため、既存の「意図的な英語発話」判定の意味が変わり、過去の全記事への影響再検証が必要) | 弱める方向のリスクあり(「記事のKey Phraseに関連する語なら日本語文中どこでも許可」という一般化は、当初「この1箇所だけ意図的に英語発話させる」という限定的設計から逸脱する) |
| C | Writer側の日本語Support生成規約へ「日本語文中で英語略語を裸のまま使わない(例:AI→人工知能)」を追加 | 低〜中(「AI」はテーマの主題語であり、日本語話者にも定着した表現のため不自然な言い換えになりやすい。Trend系記事は今後も技術略語を扱う可能性が高く、汎用対策としてはスケールしない) | 高(Prompt変更は`APPROVED_FOR_PRODUCTION`が必要な範囲が広く、既存全テーマへの遡及影響検証も必要) | 遅い(Prompt回帰確認・全既存テーマへの影響評価が必要) | 中(Prompt変更は他の日本語表現全体に波及し得る) | Gate自体は無変更だが、Writer側で毎回新語彙が出るたびに規約を追加する運用は持続可能性が低い |

**推奨**: A案。理由は、(1)費用¥0・実装最小・既存の登録手順(2026-08-26に
7語追加した時と同一手順)をそのまま踏襲するだけで新しいルール・新しい
コードパスを一切追加しない、(2)ER-009 Gateの安全目的(確信が持てない
tokenはHuman Reviewへ)を弱めない、(3)B案はGateの中核ロジック変更で
回帰リスクが高く、C案はスケールしないため。ただし、辞書へどの語を
どこまで追加するか(「AI」1語のみか、IT/EV/IoT/DX等も予防的に含めるか)は
Production辞書への追記であり、`APPROVED_FOR_PRODUCTION`のユーザー承認が
必要。

## 5. 最小Trial設計(実行しない、¥0)

1. (ユーザー承認後)`er003_audio_tts_asr_safety.py`の`DEFAULT_JA_READING_
   DICTIONARY`へ`"ai": "エーアイ"`を追加する1行編集のみ実施。
2. 新しいTTS/API呼び出しは一切行わず、`classify_foreign_tokens_in_
   japanese_text()`を、既存artifact`er011_output/family_a_trend_ai_
   manufacturing_prod_run_01/a2/a2_support_texts.json`(preview/comment_1〜4)・
   `japanese_title`(該当文字列)・`key_phrases/keywords_canonicalized.json`
   のkp5 `japanese_gloss_tts`に対して、pre-flight相当でローカル実行するのみ
   (import済み関数を直接呼ぶだけ、LLM/TTS API呼び出し無し、実費¥0)。
3. 7segment全てが`HUMAN_REVIEW`0件(japanese_title/preview/comment_1〜4は
   `READING_DICTIONARY`、kp5は`ENGLISH_PRONUNCIATION`(used_form一致、
   既存動作)または`READING_DICTIONARY`の組み合わせ)になることを確認する。
4. ここまでの確認がPASSした場合のみ、実際のTTS再生成(A2の該当7segment、
   概算追加費用は前回レポートの`tts_a2(部分)¥22.64`の残り分と同程度、
   数十円規模)を行うかどうかは**別途のユーザー判断・別タスク**とし、本
   reconcileタスクの範囲では実行しない。

## 6. 結論(7項目形式)

`docs/pm/RESULT_PACKET_TREND_RECONCILE.md`参照。
