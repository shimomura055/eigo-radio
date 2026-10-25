# OPEN333_E4_EVAL_01(E4・E4-N の API 0 評価。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_13、2026-10-26)
再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_06.py`(出力=`open333_e4_eval_01.out.json`/`.out.txt`)。**決定性(K10): 2回実行でjson sha256 `7814c7d96c90739b6feb606f0dee7f4100f994d7b3020eade5085550a5987318` 同一**。API 0・実費0円(socket guard、LLM/ASR/TTS呼出0)。事前登録=`OPEN333_E4_PREREGISTERED_01.md`(評価前に凍結。改訂なし)。
比較基準=**E3適用済みHEAD**(評価時 git `81e70d4f0`)。母集団1,638行 = 実データ+合成負例1,327 / M-3 sweep 40 / 旧v2 sweep 29 / E4行242(既存170+追加72)。

## 1. 合否(事前登録K1〜K11)
| 基準 | E4(F05=F06) | E4+E4-N | 備考 |
|---|---|---|---|
| K1 非PASS→PASS | **0** | **0** | 全1,638行・全arm |
| K2 違反遷移(PASS→即NG/Cascade→即NG) | **0** | **0** | 変化は『→Cascade』のみ |
| K3 固有名詞負例のPASS | 合成neg110: HEAD PASS **46**→**0** | 同 | 前回の96/110は数値entryが未閉鎖だった頃の値。E3適用後HEADでは非数値entryの46/55が便乗PASS(数値entry 55件はE3で既に0)。ひらがな濁点差neg_hira 50件はHEAD PASS **0**(便乗PASSを再現できず、§3.2) |
| K4 実データのPASS→Cascade | 4/676 = **0.592%** (≤1.0%) | 同 | §3.1。全4行を列挙 |
| K5 ctrl/範囲外 | ctrl変化0、out_of_scope16件不変 | 同 | |
| K6 E4-N | — | (i)cost数値entryの即NG 14→0 / (ii)混在型6件不変 / (iii)値DIFF行の変化0 | **ただし§2の重大な性質あり** |
| K7 Secondary受理 | 受理変化**0**(保存103対・全Primary転写1,203対) | 0 | ラベル変化は全Primary転写でE4=4件(実データ4行と同じ)。受理集合は不変 |
| K8 一致 | HEAD vs 前回E3V不一致**0**(1,327行)、F05_E4≡F06_E4 **1638/1638** | — | proto_05とproto_06のE4は同一挙動 |
| K9 保存Secondary転写193行 | 判定変化0・非PASS→PASS 0・PASS→非PASS 0 | 同 | 変化4行(実データ)には保存転写が無く、補足の注入で確認(§4) |
| K10 決定性 | 一致 | 一致 | |
| K11 API 0 | 0 | 0 | |

## 2. E3適用後HEADとの差分種別(全件、母集団1,638行)
| arm | 不変 | PASS→Cascade | 拒否→Cascade(HEAD即NG→Cascade) | 同種内変化(Cascadeのままラベル変化) | 違反 |
|---|---|---|---|---|---|
| E4(F05/F06) | 1,564 | **74** | 0 | 0 | 0 |
| E4-Nのみ | 1,564 | 0 | **44** | 30 | 0 |
| E4+E4-N | 1,490 | 74 | 44 | 30 | 0 |
- PASS→Cascade 74 = 合成neg txt 46 + 合成cost txt 23 + 合成cost num 1 + **実データ4**。
- **E4-Nの44行は全て HEAD の `NG_EXCLUDED / p2_exclusion:A4_C2_HOMOGRAPH`**(同形異音候補の除外=2026-10-11ユーザー逐語採用の安全条件)。同種内変化30行はHEADで既にP3(Azure)へ行っており、TRUE_CONTENT_MISMATCH→UNCERTAINのラベル変更だけ(最終判定不変)。実データ(1,327行)でのE4-Nの変化は**0行**。→ E4-Nの実効は『数値entryのA4除外の解除』。設計 §4。

## 3. 内訳
### 3.1 実データ(1,327行)で動く4行(E4・全て entity_like。すべて PASS→Cascade)
| # | canonical / ASR(Primary) | 差 | 区分 |
|---|---|---|---|
| 1 | 走れメロス / 走レメラス(Z melos タイトル、`er026_output/.../customb8f0ff16.json:japanese_title`) | ロ→ラ | (a)**本物の読み違い疑い** |
| 2 | 『…MetaのMuseで起きたまさかの展開』/『…メタのミューゼンロを着た真逆の展開』(`er033_output/phase2_ja_evidence_01/result.json#s4`) | meta→メタ、museで起き→ミューゼンロを着 | (a)**転写が崩れた本物の誤り疑い** |
| 3 | 『ヴェラは、叔母が…』/『ベラは、叔母が…』(`the_open_window comment_2`) | ヴェ→ベ | (b)正常音声のCascade送り(等価表記) |
| 4 | 『…Metaが一時停止した…Mu…』/『…メタが…ミュー…』(`comment_3`、X meta) | muse→ミューズ | (b)正常音声のCascade送り(等価表記) |
- 負例以外のHEAD PASS 676行のうち 4行 = **0.592%**。負例(N1/N3/SYN)側の実データPASS数はHEADから不変。sweep(M-3 40+旧29)は全arm不変。
### 3.2 合成負例(`sweep_cases_open333_e4_01/02.py`)
- neg(カタカナ/略語の読み違い+Eが救う同音差)110件: 非数値entry 55件でHEAD PASS 46 → E4で**PASS 0**(46件全てCascadeへ、9件は元からCascade/即NG)。数値entry 55件はE3で既にPASS 0。ラベル別は全て『HEAD PASS 3〜5 → 0』(`kata_vowel`・`acronym_*`・`kata_consonant`・`voicing_only_kata`)、`kata_shape(ミューズ→ミーザ)`はHEADでもPASSしない(delete差が混じる)。
- neg_hira(ひらがなのみの濁点差+同音差、前回未検証)50件: **HEAD PASS 0**。便乗PASSは**再現しなかった**(E4/E4Eの差も出ない)。理由(推測): ひらがなの濁点差は既存の全文読み判定(`er007_ja_asr_validator_01.py`の`whole_text_voicing_equal`)が先にCascadeへ回す。E4が濁点差(phonetic_uncertain)を含めるのは承認済み仕様どおりの完全性のためで、実測効果はない。
- ctrl 10件(名は同一): 変化0。out_of_scope 16件(乗り物なし数値entry): 全arm不変。e4n_keep_reject 6件(cascade差+しわ→すわ型の混在): 全arm不変(混在は拒否のまま、HEADでもP3)。
### 3.3 正常な等価表記(cost 50件=txt25+num25)のCascade行き率
| entry | HEAD | E4 | E4+E4-N |
|---|---|---|---|
| 非数値(25) | PASS 24 / Cascade 1 | PASS 1 / **Cascade 24 (96%)** | 同 |
| 数値(25) | PASS 1 / Cascade 10 / **即NG 14** | PASS 0 / Cascade 11 / 即NG 14 | PASS 0 / **Cascade 25 / 即NG 0** |
- 合成の正常等価表記(ヴェ↔ベ・ヴァ↔バ・NASA→ナサ・IBM→アイビーエム・muse→ミューズ)は、E4後、ほぼ全てCascadeを経る。実データの等価表記は4行中2行(0.30%)。
- 数値entryの即NG 14件(全てA4除外)はE4-Nで0になる(解除による)。

## 4. 補足(事前登録外): Cascade後の判定が既存どおり動くことの確認(`eval_open333_e4_inject_01.py`、`open333_e4_inject_01.out.txt`)
実データ4行にAzure応答を注入(stub、ネットワーク0)。HEAD=全て `PASS/primary_pass`。E4後:
- A: Azureが原稿どおり(canonicalと同一)→ **PASS_WITH_WARNING / secondary_confirmed**(再生成なし、事後試聴リスト対象)×4。
- B: AzureがPrimaryと同じ誤り→ **NG_BOTH / secondary_not_accepted**(既存の再生成経路)×4。
→ 読み違い疑いの2行(走レメラス等)はAzureが原稿どおりに聞き取らない限りPASSしない。正常等価表記2行はAzureが原稿どおりなら再生成なしで採用される。Azureの実一致率は未測定。

## 5. QCD(事実と推測を分ける)
| | E4のみ | E4+E4-N |
|---|---|---|
| 品質(事実) | 便乗PASS(合成46/55→0、実データ2件の読み違い疑い)をCascadeで検証。Primary PASS集合は縮むのみ | E4と同じ。+数値entryの合成A4除外14件がCascade可能に(安全条件A4の解除) |
| Cascade増(事実) | 実データ 4/676=0.592% × 0.2667円 = **0.0016円/セグメント**(1,327行ベース) | 同じ(E4-Nは実データ0行) |
| 再生成減(事実) | 0(増の側: 正常等価表記でAzureが原稿どおり出さない場合のみ再生成。上限は+0.59pt[4/676]、実際は未測定) | 実データ0。合成の数値等価表記14件(A4即NG)が再生成→Cascadeに |
| 納期 | 変更は1箇所+定数+監視field(約+10行) | +約25行、Opus条件(A4接触)の追加確認が必要 |
| 推測 | 月あたりの影響は小さいが、固有名詞の読み違い(ユーザーが最も重視)の取り逃しを減らす | 実害0のため効果は見えない |

## 6. 推奨(事実に基づく見立て)
- **E4のみ適用を推奨**。K1〜K5・K7〜K11を満たし、実データのPASS→Cascadeは0.59%(0.0016円/セグメント)。
- **E4-Nは見送りを推奨**。実データ影響0行、便益は合成の数値entry正常等価表記のみ、効果の本体は安全条件A4の解除(『PASSを広げる変更は不可』に最終判定の到達可能性の面で抵触)。ユーザー判断が要るのは、E4後の正式runで数値entryのA4即NGによる正常音声の再生成が実際に確認され、A4自体を見直したい場合のみ(その時点で判断候補D)。

## 7. Secondary受理(M-2)
保存対103: ラベル変化0・受理変化0。全Primary転写1,203対: ラベル変化 E4=4 / E4-N単独=0 / E4+E4-N=4、受理(SCG_PASS・orth)変化は全arm**0**。
