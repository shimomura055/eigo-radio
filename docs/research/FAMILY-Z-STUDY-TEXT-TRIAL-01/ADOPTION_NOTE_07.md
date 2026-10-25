# ADOPTION_NOTE_07(Trial-07結果に基づく現状Status候補・改善見込み・開示事項。Fable判断の材料。ユーザー決定ではない)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12 / 日付: 2026-10-25 / `ADOPTION_NOTE_04.md`・`ADOPTION_NOTE_06.md`を置換せず追補する。Production採用・配線は未承認(`APPROVED_FOR_PRODUCTION`は人間のみ。本Trialは合格しても到達上限VALIDATED)。**Part 1(案α)はユーザー正式採用済み、Part 2はTrial段階であり、両者は別物**(Part 1の配線は別agent担当)。

## 1. 現状Status候補
- **Part 2(最大1件/0件方式): 事前登録基準で不合格(Trial-07 Step A'': 8作品中7合格)。VALIDATEDにはできない。** Step Bは終了条件により未実行。
- 候補の分類(最終はFable): 「REJECTED」とするには改善見込みが高く、「VALIDATED」とするには事前登録上不合格のため、**`USER_DECISION_REQUIRED`候補**(Fableが付与判断)。分類: D(真に新しい判断=追加Trialの要否・登録の扱い。承認済み仕様の枠内の技術問題ではない)に近いが、承認の範囲(Trial-07は1回承認)を超える追加Trialを要するため、実施するならユーザー判断。
- Part 1・3・4: Trial-04の判定のまま(本Trialは対象外)。

## 2. 不合格の原因と改善見込み(根拠の観測値)
- 不合格は走れメロスr1 1標本のみ: `Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.`(POSTMOD、`misread_target=MODIFIEE`、`teaching_value=HIGH`、`OUTPUT_07_melos_r1_STEPA_DEV.json`)。同作品r2は0件。原因は2層: (1) 事前登録でこの文を「分詞の基本用法・付帯状況の基本形」として許容集合∅に含めたが、文は`with his walking stick`の修飾先が実際に二通りに読める構造的曖昧さを含み、LLMがPOSTMOD+HIGHとして挙げた(Sonnet所見: 学習価値が全く無いとは言えない)。(2) 中クラスはPrompt/コードの条件(`misread_target`・`misread_quote`・`teaching_value`)をすべて満たしたため、決定論規則では排除できない。
- Trial-06の主因(Before/After+節のFRONT 10件、ELL 3件)は**解消**(FRONT・ELLの許容集合外0)。中核の見落とし0、二十年後は0件で正処理、強クラスは全標本で中核を選定。
- 事後分析(`posthoc_07.py`/`posthoc_07.json`。合否に使わない・事前登録外・追加Trialの設計ではない): 「強クラスのみ」にするとメロスは0件で正しいが、退屈と攻撃性が2標本とも0件になる(中核P5/P7が`HEAVY`/`FRONT`で先に挙がり、同一文の`CMP`のfeatureが重複判定[`duplicate`、先に出たクラスを残す]で除外されるため。分類を優先順位でマージしない現行の重複処理の欠陥)。重複処理をクラス優先でマージすれば強クラスのみ方式は8/8に届く見込みだが、**未検証の仮説**(新標本が必要)。
- 改善見込み(自己評価): 規則の主構造は有効。残る課題は (a) 中クラス(特にPOSTMOD)に平易作品で適格が1件出る揺れ、(b) 同一文の複数分類の重複処理。成否はN=2のため確率的で、見込みは中〜高(Trial-06の4/6不合格から8作品中1作品1標本の不合格へ改善)。

## 3. 次の一手の候補(QCD付き。判断はFable/ユーザー)
| 案 | 内容 | Q | D | C |
|---|---|---|---|---|
| T1 | 追加Trial(Trial-08): 重複処理をクラス優先マージに修正+中クラスの扱い(POSTMODを平易作品で抑える等)を事前登録し、新ホールドアウトを含め再検証 | 規則の主因は解消済みで、残課題の検証が可能 | 追加Trial1回(約1時間級) | 約6〜8円 |
| T2 | 事前登録の許容集合をメロスP11を「可」へ再登録(事後変更)して7→8/8とみなし、VALIDATED候補として扱う | 事後変更=合否の根拠にならない。ユーザー承認済みの品質基準・評価の事後緩和に当たりうるため単独では不可 | 即時 | 0円(ただしStep B実物未取得) |
| T3 | Part 2を現状の運用判断に委ねる(Step Bは未実行のままPart 1・3・4を優先) | Part 2の安定した1件方式は未確定 | 即時 | 0円 |
Sonnetの推奨: 事前登録基準に忠実にT2は不可とし、T1またはT3をFable/ユーザーが選ぶ。T1は終了条件(自動追加Trial禁止)により、実施にはユーザーの明示的な承認が要る。

## 4. 量産単価(Step B未実行のため推定を含む)
- Step A'' 18 call実費5.984円 = 平均**0.332円/call**(1セット=1作品あたりStep A'' 1 call)。Step Bは本Trialでは未実行(未確認)。Trial-04実績のStep B(1選定あたり4点解説)は約0.2円級と見込むが本Trialの実測値ではない。**推定0.5〜0.55円/セット**(70円目標の約0.8%以下)。選定0件の場合はStep B call無しで0.33円/セット。
- Trial-06の0.492円/call(Step A'')から約33%削減(欄の削減と features 数の減少による出力トークン減)。

## 5. 開示事項(VALIDATED報告時にユーザーへ開示する価値判断・限界)
- 「どの構文を教えるか」の価値判断は、LLMではなく設計(固定優先順位 INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS、FRONT採否条件、`teaching_value`=HIGH要件)に置いた。事前登録で固定。
- 許容集合は主観を含む(Sonnetが生成前に本文を読んで作成。迷う文は「どちらでも可」)。新ホールドアウト2作品の許容集合も同様。
- 標本数が小さい(8作品18標本、N=2〜3)。統計的な安定性の保証ではない。
- 引用連結対策`resolve7`は本番(有料)実行では発火しておらず、Trial-06の固定データによる回帰テストでのみ実証。
- `teaching_value`は同一LLMの自己申告であり、独立した学習価値の評価ではない(強クラスの`teaching_value`=LOWによる落ち方は告げ口心臓r2の1件のみで、歯止めとしての効果は限定的)。
