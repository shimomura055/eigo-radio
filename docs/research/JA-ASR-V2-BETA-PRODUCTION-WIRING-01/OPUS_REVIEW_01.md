# Opus条件Aレビュー(逐語、2026-10-29、Fable受領。転写から機械抽出)
# OPUS独立技術レビュー: JA-ASR-V2-BETA-PRODUCTION-WIRING-01(条件A、配線設計の実装前)

## 結論
- 設計の骨格は妥当。具体的には、JA adapter(日本語ASR判定の入口関数)内の4 seam(差し込み口)、`unified_judge`無改変、scope X/Y/Z限定、PASS_Wを既存PASS_WITH_WARNINGに載せる非ブロッキング化、registry共通源、の5点。
- 実装前に直すべき欠陥が6件ある(M-1〜M-6)。主因は、βがSecondary(Azure)を追加で1回呼ぶ経路と、長さ判定・再利用判定との接合部にある。
- 論点3(PASS_W非ブロッキングによる誤PASS)について:
  - T2型は、承認済みの正例ms_03 a3と同じ構造をしている。証拠の強さはms_03 a3「以下」ではなく「以上」である。
  - したがって、ユーザー決定(4本PASS_W/2本HR)を変えずに、実装側でT2型だけを受理面から外す方法は存在しない。
  - とれる是正は監視と報告の精度向上に限られる(R-5、R-6)。

---

## 必須修正(M-)

### M-1. βの追加Secondary呼出がcircuit breaker(連続失敗時の自動遮断)を尊重していない
- 根拠:
  - 設計§4-S2-1は「circuit openは`_secondary_fn`/rsで尊重」と書いている。
  - しかし`_secondary_fn`(`er007_ja_secondary_asr_01.py:652-668`)はcircuitを見ていない。circuit判定は`unified_judge`内の`er078_asr_unified_judge_01.py:665`にしかない。
  - P1型(`p1_value_diff`、`:642`)は`:665`より前でreturnする。このためβの呼出はcircuit判定を一度も通らない。
- 変更案: `maybe_beta_rescue`の冒頭に、次の早期returnを置く。
  ```
  rs = ctx.run_state
  if rs is not None and rs.circuit_open: return jr  # 元のNGのまま
  ```
  あわせてaudit(判定の監査記録)に`ja_v2beta.beta_skipped="circuit_open"`を記録する。T-B2にこのケースを追加する。

### M-2. βの追加呼出の費用・呼出回数が記録から漏れる
- 根拠:
  - `unified_judge`は実呼出時に次を更新している: `audit["cost"]`、`rs.est_jpy_total`、`rs.secondary_calls`、`rs.secondary_consecutive_failures=0`(`er078:684-689, 711-713`)。
  - P1型ではこれらが一度も走らない。そのままでは「Azure 0回・0円」と記録され、量産単価の実績(USER §3-5)が過少になる。
  - さらに`er007:786`の`azure_real_calls`は`sec.get("called")`を読む。βがaudit["secondary"]の`called`/`cached`を正しく書かないと、`secondary_ran`(`:695`)と診断用の`steps`も欠落する。
- 変更案: β内でcache呼出が`was_cached=False`だったときに、次をすべて更新する。
  - `audit["secondary"]`の`called`/`cached`/`text`/`label`
  - `audit["cost"]`
  - `rs.secondary_calls+=1`と`est_jpy_total`
  - 成功時は`consecutive_failures=0`
  
  失敗時は判定を元のNGのまま保つ。circuitへの計上は設計どおり「しない」でもよいが、R-2を参照。T-B5に「audit cost・rs集計が実呼出と一致する」を追加する。

### M-3. 長さ判定NGのattemptをβが救済すると、判定と呼出元の結論が食い違う
- 根拠:
  - `final_length_ok`(`er078:161-176`)は、`adopted_from=="secondary"∧adopted_ok`のときしかPrimaryのlength_okを上書きしない。
  - βは`adopted_from="primary"`のままである(設計§4-S2-3)。
  - このため、Primary転写が長さNG(`length_ok=False`、またはa3有効時の`audit["length"]["primary_ok"]=False`。後者は`er078:592-595`でP1 returnより前に記録済み)でも、βが`jr`をPASS_Wにしてしまう。その結果、次の状態になる。
    - adapterは`verified=True`・`human_review_required=False`(`er007:735-764`)
    - 呼出元は`verified=False`(`repro01:413-414`/`n3_tts:847-848`)
  - 最終slotでも`_log_human_review`(`er007:809`)が呼ばれない。`verdict="PASS_W"`がNG attemptに付き、registryの記録と実際の結果も食い違う。
- 変更案: β発火条件に次の2点を追加する(長さ判定はPrimary由来、というfail-closedの原則どおり)。
  - `length_ok is True`
  - `(audit["length"].get("primary_ok") is not False)`
  
  testでは、max_len指定あり/なしの両方で「Primary長さNG+β成立形→元のNGのまま」を固定する。

### M-4. Store再利用時の再判定で、配置・API 0・版の扱いが未確定
- 根拠と問題:
  1. **配置**: 寄与ブロックは`guard_entry`の`kp_vote_gate_follows`早期return(`er078_reuse_value_guard_01.py:81`)より前に置く必要がある。ortho/UKUSの前例(`:71-80`)と同じ位置である。後ろに置くと迂回できる。
  2. **API 0**: v2の再判定に必要な`cls`は`classify_ja_asr_match`から得る。この関数は既定でReading Resolver(LLM呼出)を使い得る。J11がPrimaryを再導出しない理由そのものである(`er019_family_x_validation_inheritance_01.py:262-264`)。設計の`rejudge_contributed`は、`allow_reading_resolver=False`の明示とsocket guard testを欠いている。
  3. **版の扱い**: Resolverなしで毎回再判定すると、本番時(Resolverあり)と分類がずれる。その結果、正しいv2資産が「再判定NG→再生成」されて費用が出る。
- 変更案:
  - ②を次のように変える。
    - `judge_rule_version==現行`かつscope内 → 保存判定を信頼し、再判定しない(J11と同じ方針)。
    - 版不一致 → `allow_reading_resolver=False`でAPI 0再判定し、NGなら再生成。
  - 版の付け忘れを防ぐため、新moduleの判定核のソースhashと`JUDGE_RULE_VERSION`の対応をtestで固定する。版を上げずに判定核を変えるとtestが落ちるようにする。
  - J11継承(`er019…inheritance:207`)・resume(`er019 runner:1260`)・Z(`er063:863`)・C(`er013:444`)はすべて`guard_entry`を通る。このため上記1箇所で論点4の「版違い救済の黙認」は塞がる。
  - β資産の再判定では、auditの`secondary.text`(= `_j11_adopted_judgement`の採用転写、`er019…inheritance:246-249`)の保存が必須である。これが欠けると採用転写がPrimaryの壊れた数値になり、`final_gate_value_diff`で常に再生成される。T-S4でβ資産のaudit["secondary"]["text"]を明示assertする。

### M-5. 新module・依存ライブラリの障害時の扱い(fail-closed+A/B/C保護)
- 根拠:
  - TEST_PLAN §0は、システムPythonに`pykakasi`が無くimportに失敗した実例を記録している。
  - v2(`pron_hira`/`_tag_pron`)は形態素・読み変換ライブラリに依存する。
  - `er007`のmodule先頭で新moduleや依存ライブラリをimportすると、依存欠落時にJA adapter全体のimportが落ちる。scope外のA/B/Cも含めて、全JA判定が止まる。
  - seam内の例外が素通りすると、TTS段が落ちる。
- 変更案:
  1. 新moduleのimportと依存ライブラリのimportは、`v2b.active`が真の分岐内で遅延importにする。scope外では新moduleを一切importしない。T-A1にimport graphの検査を追加する。
  2. S1P/S1S/S2の各seamを`try/except`で包み、例外時は従来判定(L0)へ戻す。`is_config_stop_error`は既存どおり再送出する(`er078:678-679`)。
  3. 例外時は`ja_v2beta.error`をauditに記録し、完了ブロック(§8-3)に「新方式が無効化された件数」として出す。無言で従来挙動に戻ると「PRODUCTION_WIREDだが実は動いていない」を見落とすためである。

### M-6. Secondary側v2の寄与でPASS→PASS_Wへの格上げが漏れる経路がある
- 根拠:
  - S1Sの寄与は、`unified_judge`が返した後にS3で警告を後付けする設計(§4-S1S)である。
  - `done()`のPASS→PASS_WITH_WARNING変換(`er078:561-563`)は判定確定時にしか走らない。
  - `force_secondary_agreed`(`er078:837-840`)は警告なしのPASSを返す。ここにSecondary側v2の寄与が重なると、`state=PASS`のまま新方式の警告だけが付く。これはM-2原則(新層の救済は必ずPASS_W)に反する。
- 変更案: S3で次を行う。
  ```
  if 新層寄与 and audit["state"]=="PASS": state=PASS_WITH_WARNING
  ```
  JudgeResultを再構築し、`audit["state"]`も更新する。T-W1に`force_secondary=True`のケースを追加する。

---

## 推奨(R-)

- **R-1(論点1、βの細部)**:
  - `cache.get_or_call`の結果がNO_SPEECH(`er007:663-667`、`accepted=False`。成功扱いでキャッシュされ得る)の場合は、βの入力にしない。現状でも原子列不一致で落ちるが、明示的に除外する。
  - cache呼出の例外を捕捉する。
  - βがPASS_Wにした場合は、元の`state/reason_code`を`ja_v2beta.beta.original`に保存する。
  - `audit["final_gate"]={"applied":True,"target":"secondary",...}`を記録する。registryの値ガード表示、J11との整合のためである。
  - `result["final_status"]`/`classification`をβ専用ラベルにする。現状は、`is_tcm`経路では「Secondaryが原稿と一致」というSCG文言(`er007:741-745`)になり、事実と異なる。非tcm経路では`cls_s`(should_pass=False)のまま残る(`:746-747`)。
- **R-2(論点1、circuit計上)**: βの失敗を`secondary_consecutive_failures`に計上する案を推奨する(判定は元のNGのまま)。計上しないと、Azure障害中もP1型の各attemptが毎回タイムアウトまで待つ(D悪化)。計上すれば、他segmentを技術STOPにする既存の正規挙動へ早く移れる。設計どおり非計上にする場合は、理由をT-B2に明記する。
- **R-3(論点2、どの層が救済したかの判定)**: `rescue_basis`と`contributed()`は、警告ラベルの有無ではなく「確定した通過経路」から決める。
  - 例: Primaryをv2で救済したが、AMBIGUOUS降格や長さ降格でP3へ回り、通常のSecondary受理で通った場合がある。このときPrimaryの警告(`JA_NEWLAYER_*`)は残るが、救済の実体はSecondaryである。
  - 警告は残してよい(透明性の側)。ただし`layers`には「effective/non-effective」を区別して記録する。
  - NG recordに`JA_NEWLAYER_*`が残っても、`contributed()`が真にならないようにする(`state∈PASSING`を条件にする)。
- **R-4(論点2、E3/E4の範囲)**: M-6のE3/E4判定はPrimary分類のみが対象で、protoと同一である。Secondary側v2(S1S)は`cls_s`のE3/E4を見ない。品質基準を独断で引き上げないため、既定はproto同一でよい。parity(T-P3)の際に「`cls_s`にE3/E4があるのにS1Sで救済した行」の件数だけ集計して報告する。0件でなければFable判断とする。
- **R-5(論点3、誤PASSの監視)**: T-Rの判定は件数(≤8)ではなく、**行の同一性集合**で行う。既知8行(EVAL_UNIFIED_03 §4a)以外の増分が1行でもあれば報告する。件数が同じでも、入れ替わりで別型が出ることを防ぐためである。
- **R-6(論点3、非ブロッキング後の報告順)**:
  - 完了ブロックと試聴ページで、β PASS_Wを証拠の弱い順(読み相違あり > garble説明 > 発音同一)に先頭表示する。
  - run単位の件数(`count_by_rescue_basis`+読み相違件数)をJSONに残す。
  - 加えて、`USER_DECISION_REGISTER`の#206/#207に**再提示トリガー**を登録する。例: 公開済みPASS_W(新方式)で誤読が1件でも確認された場合、または読み相違β PASS_Wが一定件数を超えた場合。
  - これは報告であってGateではない。ユーザーの「試聴必須にしない」に抵触しない。
- **R-7(論点5、flag)**: scope X/Y/Z内で`JA_V2_BETA_ENABLED=False`のときは、`ja_v2beta={"active":false,"disabled_by":"constant"}`を記録する。byte同一が必要なのはscope Noneだけである。またT-D1で`is True`をassertし、OFF化がtest失敗としてcommit上に必ず現れるようにする。`is_active_for_run()`は`er109_xz_scope_01.is_active_for_run`を流用しない。この関数はortho flagと連動している(`er109_xz_scope_01.py:92-97`)。`current_scope()`だけを読む。
- **R-8(論点6、HR一覧の情報源)**: 最終報告の「要HR」一覧は`verdict=="HR"`ではなく、実際のHR queue/Lock登録から取る。対象は`HUMAN_REVIEW_LOG_PATH_JA`と`er127.register_ja_terminal_hr`である。attempt単位のverdictと、er127の最終HR登録は一致しないことがある(M-3の類型)。
- **R-9(論点7、テスト追加)**:
  - (a) precheckの健全性: corpus全行で「`composite_judge`成立 ⇒ `precheck_composite`成立」を確認する。protoは常にSecondaryを与えていたため、T-P3ではprecheckの取りこぼしを検出できない。
  - (b) M-1〜M-6の各ケース。
  - (c) v2がPrimaryを救済したとき、`is_tcm=False`(`er007:598`)によりsignalsが計算されず、A7/A4のP2除外が素通りし得る。v2自身のA7/C2判定でこれが起きないことを固定する。
  - (d) T-NB5の静的testは`guard_entry`内の`contributed()`読取(再利用可否の判断)を許可リストに入れる。報告系以外の制御フロー参照として誤検出しないためである。
  - (e) E0は一時out_dirで実行し、Production results・Store・`HUMAN_APPROVED`記録へ書き込まないことをassertする。
- **R-10(論点8、HEADで既に失敗しているtest 5件)**:
  - 是正は配線とは**別commit**で先行させる(差分の帰属を明確にするため)。
  - 期待値を現行の実際の値に合わせるだけにしない。
    - `test_single_engine_repetition_does_not_confirm_orthographic_variant`は安全不変条件(単独エンジンの収束でORTHOGRAPHIC_VARIANT_CONFIRMEDを出さない)を検査している。`verified`ではなく、その不変条件をassertする形に直す。
    - `wiring_05`のHR Lock無変更testは、基準commitを更新する。その際、差分が承認済み変更(`6e7fa7cf5`)のhunkだけであることを確認する。
  - 是正の過程で「現行Productionが承認済み仕様から逸脱している」と判明した場合は、11-8の黙示是正にせずOPEN化する。
  - 5件の是正は配線作業と並列で進めてよい。配線側の合格基準は「HEADの失敗ID集合からの新規失敗0」で定義する。

---

## 妥当(OK-)

- **OK-1(論点1)**: adapter 4 seam案は妥当である。
  - `unified_judge`は英語/A/B/C/KP投票と共有している。P1の短絡(`er078:641-650`)を再設計せずに済み、L1(Primary側`:595`/Secondary側`:677`の値等価層置換)とL2(判定後のNGへのβ)がprotoのmonkeypatch位置と1対1に対応する。
  - S2を`:691`直後かつ`audit = jr.audit_record`(`:693`)の前に置けば、HR判定(`:750-764`)以下が新しい`jr`で動く。
  - キャッシュkeyは`ctx.sha()`/`ctx.engine`/`"ja"`/`ctx.phrase_list_hash`で`er078:663`と同一にすることが条件(nosha fallbackもctx側で吸収される)。
- **OK-2(論点2)**: 安全条件の維持は、次の5点で成立している。
  - F1+F2: 新分類を`_READING_MATCH_CLASSIFICATIONS`/`APPROVED_EQUIVALENCE_BASES`に入れない(`er007:630`でbasis=Noneになり、`er078:599-619`の最終ANDゲートを受ける)。
  - M-6: E3/E4の値を`_ce_rej/_ce_casc`(`er007:575-577`)から流用する。protoの`e34_state`と同一の入力である。
  - M-7: `phrase_list_hash==""`(`:644`)でfail-closedにする。
  - M-1: 不規則読みの検査をv2とβの両方で行う。
  - R-1(複数読み漢字の検査)はコード自体を入れない(R1-a案)。
- **OK-3(論点3、J-3)**: `secondary_reading_conflict="warn"`固定は妥当で、vetoへの変更はユーザー判断事項である。理由は次のとおり。
  - ms_03 a3はPrimary「月の氏は8000900本超」、Azure「杉野氏は8900本超」(EVAL_UNIFIED_03 `:40`)。garble説明・発音同一・読み相違の3条件が重なった、最も弱い証拠の正例である。
  - T2負例2件(Primary garbleで、Secondaryが原稿どおり)は、これより証拠が強い。T2を外す規則は、必ずms_03 a3も外す。
  - vetoにすると、決定済みの4/2(USER §3-5、`..._USER.md:139`)が3/3に変わる。
  - T2の現実的な露出は「原稿を渡されていないAzureが、誤った音声から原稿どおりの値を出す」場合に限られ、M-7と同一sha provenance(同じ音声ファイル由来であることの保証)で抑えられている。
- **OK-4(論点4)**: scope外・flag OFFのentryを再生成する方針は、ortho/UKUS/PNAPの前例(`er078_reuse_value_guard_01.py:52-80`)と同型で妥当である。A/B/Cでは再生成費用が出るが、承認範囲外の受理音声を流入させない側として正しい。
- **OK-5(論点5、J-1)**: 定数1個+読取関数1個は「迂回路」に当たらない。値の変更にはソース編集+commitが必要で、実行時の切替経路が無い(前例: `er078:80`、`er007:515`)。flagを置かない案(F2)では、Store内の寄与資産を制御できない。F1を推奨する(R-7の付帯条件付き)。
- **OK-6(論点6、J-2)**: registry(`er078_pass_with_warning_registry_01.py`)を共通源にすることは妥当である。現行でも採用音声(segment最上位)のPASS_WITH_WARNINGだけを列挙している(`:17,25,100-103`)。音声path・sha・警告・原稿・Primary/Secondary転写・reasonを持つので、`rescue_reason_ja`の追加と、Yのページ節(`er121_family_y_runner_01.py:1282`)の補完で、USER §3-2-4の3要件(対象音声・発生理由・警告内容)を満たす。旧recordのbyte互換方針も妥当である。
- **OK-7(論点7)**: TEST_PLANの骨格は十分である。月6本の4/2再現、N3の実誤読wav、汎用題とmetamorphic test、非ブロッキング、Store引継ぎ、E3/E4、scope外byte同一、静的test、が揃っている。不足分はR-9とM-1〜M-6のケースのみ。
- **OK-8**: `er109_hr_lock_rejudge_01.py`は`force_lang="en"`(`:112`)で、HR Lockの自動解除もしない(`:5-6`)。このため本件で既存のJA HR Lockが自動PASS化される経路は無い。

## 追加で必要になり得る確認(範囲外のため未読)
- `er127_tts_block_policy_01.py:726-740`(terminal HRの判定元。R-8)
- `er006_master_audio_store_01.py:130-137`(guardに渡す`_probe`が`asr_judgement_inherited`を含むか。M-4)
- `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_02.py`の依存import(M-5の対象ライブラリの特定)

## 参照ファイル
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-V2-BETA-PRODUCTION-WIRING-01\WIRING_DESIGN_01.md
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-V2-BETA-PRODUCTION-WIRING-01\TEST_PLAN_01.md
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-V2-BETA-PRODUCTION-WIRING-01\COVERAGE_MATRIX_01.md
- C:\Users\tensh\eigo-radio\er007_ja_secondary_asr_01.py
- C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py
- C:\Users\tensh\eigo-radio\er078_reuse_value_guard_01.py
- C:\Users\tensh\eigo-radio\er019_family_x_validation_inheritance_01.py
- C:\Users\tensh\eigo-radio\er078_pass_with_warning_registry_01.py
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-FIX-02\proto_unified_03.py
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\b_light_proto_02.py
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-FIX-02\EVAL_UNIFIED_03.md

Production採用の可否は判断していない(本件は承認済み仕様の配線レビュー)。実装・修正には着手していない。
