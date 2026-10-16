# FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 Opus独立レビュー所見(read-only、JPY0、到達=所見)

## 総評
監査の骨格は概ね妥当です。§1の結論「一部」、Sol統一の配線、承認済み6仕様が未配線であることは、現物と一致しました。一方で次の4点は修正が必要です。
- **ユーザー判断事項の過大計上**: (d)(e)と P1-3 は、既存の承認でカバーされています。
- **承認範囲の拡大が混入**: (i)の新しい既定profileに、Coffee限定承認の E1/R2 が含まれています。
- **retry経路の見落とし**: Local Rewrite が In One Line(以下IOL)を「one-line summary」と記述しています。
- **SSOT(CURRENT_SPEC)の09:00小節自体に事実誤り**: 現行Full StoryをP8と記載していますが、実際はN01です。

Fableの暫定評価への見解は次のとおりです。(a)(b)(c)(g)(h) と P2先行は同意します。(i) は条件付き同意(4仕様部分のみ)です。(d)(e) は不同意です。

## Q1. §1〜§4の判定は証拠から導けるか → 条件付き同意
**現物で一致した点**
- adv:558 `- Exactly one sentence.` と、adv:565-567 のTrial限定文言。
- style_profile:16-17(K2/M2 は後続Phase)と :110 `DEFAULT_NEW_RUN_PROFILE=PROFILE_N01`。
- routing:134,137,138(Sol をリテラル固定)、:48-50,105,110(英語化は Luna)。
- w1:66,95(規則7)、w1:131-139(AN3 第1文を置換)。

**過大評価・不正確な点**
- **FXWA-R-01(中)**: §1表2行目「Fact Lock・Prompt sha不変=Yes(問題なし)」は言い過ぎです。verbatim_shas は**定数のsha**です(監査自身も§11-4でAN3について認めています)。ユーザー指示§5F は「runtime入力との比較」を求めています。正しくは「コード定数レベルでは一致。実際に送信された文は保存されておらず未確認」です。
- **FXWA-R-02(低)**: §2 #5 と §7 P1-1 は「Comment4がIOL生成と矛盾」としていますが、これは誤りです。Comment4 は B1(audio_plan:201-203)も A2(:234-236)も「1文とは限りません、文数を断定しない」と書いており、文数に依存しません。2文化した後もそのまま整合します。引用行の 206-208 も誤りです。したがって Comment4 の改修は Blocking から外せます。
- **FXWA-R-03(中)**: §2末尾の「配線済み・問題なし」に「KP解説(P3)」が入っています。P3 は09:00にP7へ置換済みなので、陳腐化した判定です。
- **FXWA-R-04(中)**: 監査は CS:1236 の「現行Coffee Production Full Story=P8」を見逃しています。現物は N01(style_profile:85-90,157,161,169、2026-10-13 Family X/Z承認)です。さらに、PD06 が N01 を Family X で置換すること(Family Z は N01 のまま)が、CS:1244「旧決定との関係」に書かれていません。旧決定として記載があるのは PD8→P8 だけです。
- 推測によるPASSは、Sol の retry 未発火と正式W-1 Coffee の未実走を監査が自分で「未確認」と明記しており、適切です。

## Q2. §8(a)〜(i)の分類(A=承認済み / B=自己解決可 / C=独立問題 / D=真のユーザー判断)
| 項目 | Opus判定 | 理由 |
|---|---|---|
| (a) P7正本 | **D(軽い確認)** 同意 | 同じ名前の別P7が実在します(CS:1239)。(b)の名称対応と合わせて、Yes/No 1問にまとめるのを推奨します。 |
| (b) PD06=PD6 | **名称対応はD(軽い確認、(a)と同じ問い)**。Std への同一文適用は **A** | ユーザー原文が「Full Story TTS(Std／Adv)=PD06」です。PD06 の表記は09:00の文書以外にありません(Grep)。 |
| (b) Std の6%減速併用 | **B** | Family X の Std は「逐語+生成後6%減速」が既定の慣行です。P8 は S1例外(style_profile:20-28)、N01 は2026-10-13のユーザー決定に含まれます(:81-82,140)。同じ方式を採り、ユーザー報告では「採った方式」として明示します(問いにはしません)。ただし PD06 には N01 の「a little slower」に相当する速度語がないため、Adv の速度変化は Coffee 試聴で確認する事項として書きます。 |
| (c) IOL 2文Prompt | **D** 同意 | 改修自体(「旧1文Promptを改修する」)は判断済みです。承認が必要なのは文面と「必要時3文」の基準だけです。案と少数のoffline出力サンプルを添えて、1回で承認を取るのを推奨します。 |
| (d) 英語化モデル | **不同意 → C** | 現状の Luna は判断7(DL:20263)でカバーされています。routing:105,110 も当時の承認済み Luna で配線されています。承認漏れではなく、任意の改善候補です。USER_DECISION_REQUIRED にはせず、独立した改善候補として起票します。 |
| (e) AN3第1文の置換 | **不同意 → A(+SSOT是正はB)** | 承認Trialそのもの(`er052_factlock_writer_trial_01_run.py:6,104-111`)が同じ置換を行っています。w1 はそれを移植したものです(w1:65)。ユーザー指示§6が「承認済みFact Lock構造」を再判断対象から外しているので、追認を求める必要はありません。 |
| (f) OPEN-243の守り | **C → (h)の一括整理に統合** | 守りの撤去は承認済みの RF配線(CS:1182)の帰結です。残る論点は OI を継続するか close するかだけです(本監査では close を独断できないので、一括の問いに入れます)。 |
| (g) Hook | **D** 同意 | ユーザー指示§5Dの「過去決定が後続仕様で失われた」に該当します。廃止にはユーザー判断が必要です。Blocking ではありません。 |
| (h) 一括整理 | **D** 同意 | (f)を含めます。R23 と R22 の結果記録は B です。 |
| (i) 既定profile化 | **分割**: PD06/K2/P8/P7 を既定にするのは **B**(Fable判断可。根拠=FX記録§1/§3「Family X全体」)。**E1/R2 を Family X の既定に入れるのは D** | 09:00の表に E1・R2 はありません。CS:1244「Coffee限定だった各Style承認(OPEN-298/300)は本判断で Family X全体へ拡大」は記録者の解釈で、ユーザー原文§1の「以下は…Coffee限定仕様ではない」は表の項目に限られます。要約で承認範囲を広げることになるので、要確認です(**FXWA-R-05、高**)。 |
| P1-3 R0規則7 | **A(対応不要)** | 承認Trial `er052…:51,82,100,111` に同じ規則7があります。承認済みの逐語shaの一部です。削除すると承認済みPromptが変わるため、P1から外し、OIに注記するだけにします。 |

## Q3. §9 Blocking の必要十分性 → 条件付き同意(追加3件・修正2件)
**残すもの**
- 1 IOL
- 2 四つのStyle(前提として(a)の確認)
- 3 既定profile(4仕様のみ)。Coffee が CLI 限定の経路で検証されると、代表記事として成り立たないためです。
- 4 OPEN-343: 着手前に triage し、Std Coffee で発火しうるものだけを Blocking にします。
- 5 実走時の確認項目: 事前の作業ではなく、再制作そのものの Gate 項目として扱います。

**追加するもの**
- **FXWA-R-06(高)**: IOL の retry 経路。`er020_tts_retry_local_rewrite_01.py:158` が IOL を「the closing one-line summary」と記述しています。TTS の ASR NG による Local Rewrite で、2文が1文に戻るおそれがあります(ユーザー指示§5C「部分配線」型)。Blocking 1 の範囲に、ラベルの改修と文数保持の test を含めてください。Std の継承 test(監査§4-9)も同じ範囲です。
- **FXWA-R-07(中)**: Master Audio Store のキーは `style_instruction_id`/`version` を含みます(`er006_master_audio_store_01.py:37,48-49,141`)。K2/P8/P7/PD06 を配線するときに既存の id/version のまま文言だけ変えると、旧Styleの音声が再利用されます。新しい id か version を割り当て、test で固定してください。
- **FXWA-R-08(中)**: style_profile には既に `P8_TEXT` があり、中身は Full Story P8(:48-56)です。KP日本語意味の P8 を配線するときは、別の定数名と別の role にしてください。ROLE_SEGMENTS(:121)は今「Key Phrase日本語意味・IN_ONE_LINEは対象外」となっています。混同を防ぐ test も必要です。

**修正するもの**
- Comment4 の整合は不要です(R-02)。
- 送信Promptの保存は、Coffee 実走1本分を runtime evidence として送信文の sha を記録するだけなら、09:00§4 の「runtime evidence」要件の範囲内で B(Fable判断可)です。恒久的な Production 機能や blocking QA にする場合は、仕様追加としてユーザー判断です。

## Q4. 見落としうる「良いTrial成果の未反映」
- **FXWA-R-09(中)**: Part B の範囲は B3 から始まっていて、ユーザー指示§1が対象に挙げた **Research・Fact Ledger 段**の Trial が行として存在しません。evidence 系の Trial などです。
- **FXWA-R-10(低〜中)**: 次も行がありません。Title生成、Preview/Comment1〜3 の文面系 Trial、KP 解説文(explanation_en)の生成Prompt、Std KP日本語意味の「文面」生成、そして `MAQ_TRIAL_W-1`(現行 Coffee の出所)そのものの Trial としての扱いです。KP選定は ABC だけです。
- 探索手法がDL見出しとキーワードのGrep中心なので、名前にTRIALを含まないユーザー個別指示による改善の拾い漏れが残りえます。委任ログ(USER.md)のファイル名で10/1〜10/16を総当たりする補完を推奨します(JPY0)。
- 本レビューの範囲内では、新しい「良好かつ未承認」の成果は確認できませんでした(網羅は未保証)。

## Q5. SSOT是正(P2)の先行 → 同意(B)。注意点は以下です。
1. 旧行は削除・書き換えをせず、【置換注記 日付/管理ID → 最新pointer】を追記します。ユーザー決定の Status タグは変えず、注記だけにします。
2. CS:1236 の「現行=P8」を N01 に訂正します。CS:1244 に「Family X では N01→PD06。Family Z は N01 を維持」を追記します。
3. CS:1244 の OPEN-298/300 拡大文は、断定をやめて「E1/R2 の Family X 既定化は要ユーザー確認」と書き直します(R-05)。
4. AN3 の記述(CS:905/1169)は「定数は保持。R0 に実際に送られるのは第2文+Fact Lock規則5(承認Trial `er052…:104-111` と同一)」とします。
5. CS:583(ER-003系 IOL「中心1文+補足2文」)と CS:580 に、Family X では09:00判断が最新である旨を注記します。
6. OPEN-299 の状態タグを approved-unwired に更新します。OI は close しません。
7. 配線担当 worker と同時に編集しないでください。監査中にも並行編集で行番号がずれています。対象ファイルは明示的に git add し、1回の commit にまとめます。
8. (e)(f)(g)(h) の判断結果は先回りして書きません。

## Q6. 新たな USER_DECISION_REQUIRED
- **新規1件**: E1(Adv Preview)と R2(Std日本語Preview/Comment)を Family X 全体の既定にするか(R-05)。Coffee 再制作では Coffee 限定承認のまま使えるので、Coffee の Blocking ではありません。Family X 共通仕様を完成させるうえでは必要です。
- **既存のまとめ直し**: (a)+(b)の名称確認を1問、(c)の文面承認、(g)、(h)+(f)。
- **撤回**: (d)と(e)、P1-3 は USER_DECISION_REQUIRED から外れます。

## 指摘一覧
| ID | 重大度 | 内容 |
|---|---|---|
| FXWA-R-01 | 中 | 「Prompt sha不変=問題なし」は定数レベルの確認にすぎず、runtime入力は未確認 |
| FXWA-R-02 | 低 | Comment4の「矛盾」は誤り(audio_plan:201-203/234-236は文数に依存しない)。引用行も誤り |
| FXWA-R-03 | 中 | 「問題なし」欄に置換済みのP3が残っている |
| FXWA-R-04 | 中 | CS:1236の現行Full Story=P8は誤り(実際はN01)。N01→PD06の置換が記載漏れ |
| FXWA-R-05 | 高 | (i)にCoffee限定承認のE1/R2が混入。CS:1244の拡大解釈も同じ問題 |
| FXWA-R-06 | 高 | Local Rewrite(er020:158)がIOLを「one-line」と記述。2文→1文に戻るリスク |
| FXWA-R-07 | 中 | Master Audio Storeのstyle id/version未更新だと旧音声を再利用するリスク |
| FXWA-R-08 | 中 | style_profile内のP8名称衝突(Full Story用とKP日本語意味用) |
| FXWA-R-09 | 中 | Research/Fact Ledger段のTrialが監査範囲から抜けている |
| FXWA-R-10 | 低〜中 | Title/Preview/KP解説文/MAQ等の行がない |
| FXWA-R-11 | 中 | (e)とP1-3は承認Trialと同一なのでA。追認不要 |
| FXWA-R-12 | 低 | (d)は判断7でカバー済み。C(任意改善候補)へ |

## 確認した証拠(file:line)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_advanced_adaptation_generate.py:551-573,583-602`
- `C:\Users\tensh\eigo-radio\er019_family_x_style_profile_01.py:16-28,48-56,81-90,99-123,138-175`
- `C:\Users\tensh\eigo-radio\er053_family_x_factlock_ja_writer_01.py:62-95,131-138`
- `C:\Users\tensh\eigo-radio\er052_factlock_writer_trial_01_run.py:6,51,82,100,104-111`
- `C:\Users\tensh\eigo-radio\er006_model_routing_contract_01.py:45-51,105,110,130-138`
- `C:\Users\tensh\eigo-radio\er019_family_x_audio_plan_01.py:193-236`
- `C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py:113,143-144,152-159`
- `C:\Users\tensh\eigo-radio\er006_master_audio_store_01.py:9,37,48-49,141`
- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md:580,583,1203-1246`
- `C:\Users\tensh\eigo-radio\docs\pm\USER_DECISION_REGISTER_01.md:180-190`
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01\PART_B_TRIAL_MATRIX_01.md:14-97`
- ユーザー原文2件(`docs\pm\delegation_log\2026-10-16_FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01_USER.md`、`…FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`)

**未読(範囲外)**: PART_A §3・§5、PART_C §2・§4(監査本文の要約を照合に使用)、DL本体、OPEN-343 の詳細。CS:829-831・905・1169 は監査§11の引用で代替しました。Production採用の可否は判断していません。実装には着手していません。