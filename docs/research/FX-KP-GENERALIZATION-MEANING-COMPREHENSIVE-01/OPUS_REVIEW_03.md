# Opus独立技術レビュー(条件A) DESIGN_03 2026-10-23

(逐語保存。出典: 委任_07 §2)

総合判定: 必須修正を入れればTrialに進んでよい。方向性(一方向の伝染を断つ・案Sは不採用・B仕様の変更はVALIDATED後にユーザーへ諮る・Judge基準の修正を先に行う・段階gate)は支持する。ただし推奨の核であるE4の読み方、評価指標の定義、cacheの無効化、Std側の結論の強さに、結論を左右する欠陥がある。

[必須] OF-KPGM-D3-01 E4は2つの変更を同時に入れており、悪化はgloss除去ではなく「用法先決め」の段から来ている。根拠: kp_probe_03_report_out.txt。E1(glossを外すだけ)は sense 28/28・core 26/28 でE0と同値。E4は sense 25・core 22。KP別にE4だけで失敗: wallet(E1 111/111→E4 011/011)、pull someone under、refueling support(101/101)、apply one's findings、draw a lineのcore。E4がE1に勝つのはsingleだけ。G2(差し引き0)、E3(最悪)と合わせ「lunaに字義/比喩を明示的に分類させると誤りが固定される」仕組みが3回出ている。reasoning modelは出力前に内部で考えるため、schema順で考えさせる利得は小さく、決めた内容に縛られる害が残る。修正: Adv armを要因ごとに分ける: E0 / E1 / E1+core_sense(usage_typeなし) / E4。第一候補は最も簡潔なE1型(入力行とそれを参照する規則行を消すだけ)。E4は修正後Judgeで明確に上回った場合だけ採る。
[必須] OF-KPGM-D3-02 single指標がユーザー目標例と食い違う。er112_kp_gm_judge_01.py:54「AまたはBの併記=0」だが、目標例 "to establish a clear boundary or limit" も "or" を含む。E1/E4差(single 21→28)はこの指標依存。修正:「異なる2つの語義・用法を並べた場合だけ0。同じ1つの語義を同義語で補った場合は1」と定義し直し、probe-03既存行を再判定してキャリブレーション。
[必須] OF-KPGM-D3-03 E0基準値は改善後Std glossと組み合わせて測る。probe-03のE0はG0 gloss(「線を引く」)入力で111/111だったが、Stdが「一線を引く」になるとE0はacceptable型3/4(03b)。修正: Std armとAdv armを交差。E0は各G arm(特に採用候補G)の出力を入力に測る。E1/E4はgloss非依存なので1回。
[必須] OF-KPGM-D3-04 signatureからglossを外すとXでは旧仕様の説明がそのまま再利用される(X/Zで挙動が違う)。runner:1084-1088 phrases_signature一致でgloss条件を外せば旧Prompt説明がreuse。Zは er026:1517-1528 でsig_payload形が変わりハッシュ変化→再生成。どちらもPROMPT_SHA256・仕様versionがsignatureに無い(auditにはある er019...:360)。修正: X bundleとZ sig_payload両方に説明仕様ID/PROMPT_SHA256を入れる。既存完成記事を次回runで再生成する扱いを明記。
[必須] OF-KPGM-D3-05 撤去対象の漏れ: er019_family_x_kp_explanation_01.py:79-80 "Do not just translate the Japanese reference meaning…"(外す入力を参照)、:165-167 docstring、呼び出し側 runner:1089-1091・er026:1534-1535(japanese_gloss)、schema名 `..._trial_02`。er041(Trial-02履歴module)は編集しない。逐語一致testは「Trial-02と一致」を撤去し新仕様IDのhash固定へ置換。
[必須] OF-KPGM-D3-06 Std gate「draw a line 3/3」だがSol armは8unit×1repで1サンプルしか取れない。§6-7費用「2arm×8unit×約2円=約32円→8unitに限定して約16円」は矛盾(2armなら約32円)。Sol単価はluna 688token流用でeffort highの実測なし。修正: draw a line単体は各Sol armで3rep。難例バッチはSol arm 1本に絞るかunit数削減。Sol費用は1 call実測で再見積もりしてから進める。
[推奨] OF-KPGM-D3-07 「modelの判断力が律速」はまだ仮説。試したのはlunaのみ、Prompt変更も再整合用枠組み内の2案のみ。現Promptは既存glossの全語反映判定用(er003:580-604)、新規生成文(:315-321)も「過不足なく一致」「source_sentenceは語義選択のみ」で語単位対応へ誘導。G2は「英語中心義の言い換え」方向で「区別する」に流れた。未試行手段: 新規生成(current=null)項目だけを対象に「英和辞典の定訳や対応する日本語慣用句があればそれを、無ければ中心義を平易に言い換える」という目標種類の変更、同一call内で2〜3案を出して自己選択。修正: lunaのG3 armを1本追加(約3円)、G3-solは条件付き。few-shotにdraw a lineを入れるのは個別対策で禁止。
[推奨] OF-KPGM-D3-08 因果主張を証拠の強さに合わせる。draw a line単体は強い(3/4対0/16、Fisher片側p≈0.004)、Carry the Load(2/4対0/8)は弱い。層別はKP難度が共通原因。probe-03ではgloss除去で全体coreは改善せず(E1=E0=26/28)。確実に言えるのは「glossは含意を持ち込みうる。特に目標Std(一線を引く)はE0を悪化させる」まで(除去理由として十分)。補足: 英語 "draw the line (at)" には「許容の限界」という正規語義があり、「一線を引く」がその語義を呼ぶ面がある。
[推奨] OF-KPGM-D3-09 Std/Adv整合は「同じ用法(字義/比喩)で矛盾しない」と定義。条件付き再整合を最初から入れるのは過剰設計。Trialで矛盾件数を測り、難例で1件以上出たときだけ検討。
[推奨] OF-KPGM-D3-10 Judge: core修正案(表現の定義に含まれる語は数えず、記事の対象・目的・場面・評価条件だけを混入)は妥当。加えて: 生成前に難例20件の正解ラベル(用法と許容語義範囲)をFableが固定(Carry the Loadのように正解が曖昧な例があるため)。2系統Judgeを正解ラベルに対し校正しkappa報告。Fable目視=ランダム20%+不一致行全件。Judge再判定一致(約30行)を事前に1回測る。armは伏せて判定。Sol Judgeで系統相関の偏りを補う構成は妥当。Stdの「区別をはっきりさせる」は要求文言は満たすが「一線を引く級」かは不明→単独質問にせずVALIDATED報告に代表例を並べる。「線を引く/境界線を引く」はNG確定。
[推奨] OF-KPGM-D3-11 統計: 同armの再生成で判定が揺れるKPが25〜50%あり、基準5(非劣化95%)・基準4(100%)はE0自身が満たせない可能性。修正: 非劣化はE0とE0再生成の自己一致率を基準、許容差を事前宣言。KP単位対比較で改善/悪化/不変flip件数(McNemar型)。「5%以下」はWilson信頼区間添付。全て方向判断。75KP×3rep(約225行)で足りる。
[推奨] OF-KPGM-D3-12 ユーザー検証項目6はVALIDATED前に満たす。DEV注入(Zは er026:1537 `expl_call_fn` hook、Xも同様)でX 1本+Z 1本のtext工程E2E(TTSなし、約6〜10円)をVALIDATED前に実施、retry発動統計も取る。Production moduleのhashが開始時と終了時で同一であることを記録。
[情報] OF-KPGM-D3-13 Structured Outputsはschema property順で出力。生出力でkey位置を記録し決定論的に検査すればよい。現行は english_explanation 以外読まれない(er019...:311)ので下流不変。
[情報] OF-KPGM-D3-14 E3悪化は「1回決めた判断の固定」+lunaの判断精度不足。E3-solはSol glossが難例で用法をほぼ正しく判定した場合だけ実施(条件付き、約8円節約)。canonicalization callで意味を運ぶ案は波及大の割にE3と同じ仕組み、再検討価値低。
[情報] OF-KPGM-D3-15 Sol +約1.9円/セット(+2.7%)は妥当規模だが実測前提。25節どおり評価model/本番modelは別判断。費用低減候補: Sol armでglossの入力から記事全文を外す、Solを多語動詞句に限る(決定論振り分け)。採否比較表に載せる。慣用句辞書は費用対効果不明、G3とSolが共に効かない場合の進言候補。
一致: 主因=一方向の伝染/案S不採用/新規LLM call 0/B仕様変更はVALIDATED後ユーザー/Judge修正先決/段階gate/Production model別判断。対立: 核はE1型の要因分解(01)/single定義(02)/E0交差(03)/仕様versionをsignatureへ(04)/G3並列(07)/自己一致率基準(11)/項目6をVALIDATED前(12)。費用は修正後も60円前後。
