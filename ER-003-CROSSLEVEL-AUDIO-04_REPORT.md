# ER-003-CROSSLEVEL-AUDIO-04 実行報告(発音方式・In One Line・速度測定・Naturalness QAの整理)

**管理ID: ER-003-CROSSLEVEL-AUDIO-04**
**実施日: 2026-08-10**
**ステータス: `PHASE 1-2 COMPLETE`(調査+小規模試作のみ。完成音声の全面再assembleは未実施)**

比較試聴: [Artifactプレーヤー](https://claude.ai/code/artifact/53c4897d-c77c-49a4-973e-c59087619d05)

## 1. Go ahead語末対策の併用有無

**併用されていなかった。** 前回(ER-003-CROSSLEVEL-AUDIO-03)で採用した
"Go ahead"のcontext-aware instructionは、以下の文言のみで構成されていた
(実際に実行したコードから引用):

> "...In this recording, the phrase 'go ahead' is a sports term meaning to
> take the lead in a game... Do not add, omit, or change any words, and do
> not over-emphasize or exaggerate any single sound."

語末音素対策(`er003_v1_a2_audio_02_generate.py`の`TRIAL_CLARITY_INSTRUCTION_PREFIX`)
に含まれる「make sure the very last sound of the phrase is actually
spoken, not trailed off into silence」という一文は**含まれていなかった**。
つまり現行採用版(音素試作版)には意味prosody対策がなく、今回試作した
context-aware版には語末音素対策の明示文がなかった——両者は一度も
併用されていなかった。

## 2. 3フレーズの共通発音試作結果

意味prosody・語末音素保持・フレーズ一体感(単語ごとの区切り読みにしない)
の3条件を1つのinstructionにまとめた統合版を試作した。

| フレーズ | 統合試作版 duration | 内容(ASR) |
|---|---:|---|
| Come on | 0.711秒 | "Come on."(正確) |
| Go ahead | 0.871秒 | "Go ahead."(正確) |
| Brent crude oil | 1.711秒 | "Brent crude oil."(正確) |

3件とも内容は正確。[Artifact](https://claude.ai/code/artifact/53c4897d-c77c-49a4-973e-c59087619d05)
で現行版・前回試作版と聞き比べ可能。**自然さの最終判断はユーザー試聴。**

## 3. In One Line原因と一般化案

**訂正した前提での再調査結果。** "In One Line"は読み上げるべき見出しであり、
問題は「発話したこと」ではなく「見出しテキスト自体を本文に含めずに
生成していたため、発話が不安定だったこと」だった。

- **A01・A02**: 見出しを**発話しなかった**(指示に従わず省略、これも
  本来は不足)
- **ADD03**: 見出しを**発話したが日本語風に聞こえた**(見出しテキストが
  実際の入力に存在しないため、根拠のない状態で無理に生成し不安定に
  なった可能性)
- **B1**: 常に正常。理由は、B1は記事全体を1回のTTS callで生成し、
  `## In One Line`という見出しテキスト自体が入力に実在するため
  (実際のB1音声を切り出しASR確認: "In one line."と正常に発話)

**一般化案**: Point One/Point Twoは見出しテキスト自体を本文に含めて
生成しており、問題が起きていない。同じ方式(見出しテキストを実際に
本文へ含める)をIn One Lineにも適用したところ、**3回中3回とも
"In one line."と安定して正しく発話**された。この方式を、他の英語見出し
(Now, the full story./Here are today's key phrases.等)にも一般適用
できる候補として記録する(新しい大規模routingシステムは作らない、
テキスト構成のみの変更)。

## 4. B1/A2 WPM再測定結果(同一条件)

B1本編音声(単一連続音声)を、既存のnotification2挿入位置マーカー
(MFA/ASRで特定済み、`er003_v1_repro01/02_main_generate.py`)を境界に
Full Story/Points/In One Lineへ分割し、対応するテキストの語数で
A2と同じ計算式(語数÷音声時間×60)により再測定した。

| Article | Level | Full Story WPM | Points WPM | In One Line WPM | 全体WPM |
|---|---|---:|---:|---:|---:|
| A02 | B1 | 137.87 | 135.75 | 155.78 | **139.13** |
| A02 | A2 | 145.36 | 151.39 | 167.51 | **150.02** |
| ADD03 | B1 | 147.85 | 134.15 | 142.43 | **143.03** |
| ADD03 | A2 | 143.83 | 137.48 | 171.98 | **143.85** |

(使用音声: B1=`er003_output/b1_p8a/{A02,ADD03}/body_raw/*_dynamics3.wav`
のnotification2挿入前区間、A2=`er003_output/a2_audio_01/A02`・
`er003_output/crosslevel_audio_02/ADD03`の各segment音声)

**前回の「A2平均150 vs B1平均137」は記事構成差を含む粗い比較だった。**
同一条件での再測定では、**記事によって傾向が異なる**(A02はA2が明確に
速い、ADD03はほぼ同じ)。ただしIn One Lineは2記事ともA2が明確に速い
(短い孤立segmentほど速く読まれる傾向、既出の"孤立フレーズ"問題と
同系統の可能性)。

## 5. A2 target WPM提案

上記の通り、B1自体のWPMも記事によって139〜143の幅がある。**単一の
固定倍率(0.9x)を機械的に適用するのではなく**、以下を提案する。

- B1平均: 約141 WPM(139.13と143.03の平均)
- A2現行平均: 約147 WPM(150.02と143.85の平均)
- **A2 target案: 約125〜130 WPM**(B1平均の約89〜92%、「B1よりやや遅い」
  というユーザー意向を反映)

前回試作した減速instructionは83.7 WPMまで減速しすぎた(狙いの約束6割)。
今回のtarget(125〜130 WPM)に近づけるには、より弱い表現("just a little
slower than usual"程度)での再試作が必要。**今回はtarget提案までとし、
新たな音声試作は行っていない。**

## 6. Naturalness QA量産設計案(設計のみ、実装なし)

生成モデル自身への自己確認にしない、という要件を踏まえた設計案:

```
A2生成(既存の方式L等とは独立したstep)
  → Naturalness QA(生成と別contextの独立callで実施。
     Grammar/Idiomaticity/News narration/Meaning preservation/
     A2 suitability/Spoken-firstの6軸を文単位で判定)
  → 判定: PASS / REVISE / HUMAN_REVIEW
      - PASS: 次工程へ
      - REVISE: 該当文のみ部分修正 → 修正箇所のみ再QA(全文再QAしない)
      - HUMAN_REVIEW: 機械的に自動修正しない、人間判断へ
  → 既定試行回数を超えてもREVISEのままならHUMAN_REVIEWへ強制昇格
     (無限ループ・黙殺を防ぐ)
```

**"Simple AND Natural"の担保**: REVISE時の修正案は、既存のA2言語制約
(平均文長・最大文長・語彙の平易さ)に対する再チェックを通過しない限り
採用しない。「自然にするために語彙・構文を難化させる」ことを、
QA/修正ステップ自体の構造でブロックする(4節so参照した既存の禁止事項
と同じ考え方をQA工程にも組み込む)。

**独立性の確保**: 最低限、生成に使ったcontextを引き継がない新規callで
QAを実施する(自己弁護的な自己承認を避ける)。より強い独立性(別モデル・
別ベンダー)は将来の拡張候補として記録するに留める。

## 7. 未解決事項・ユーザー試聴が必要なもの

- Come on/Go ahead/Brent crude oilの統合発音試作が、実際に自然に聞こえるか
- In One Line修正版が、B1と遜色ない自然な英語見出しに聞こえるか
- A01の`added more time`→`The game went into added time.`への差し替え可否
  (次回assembleでの反映候補として記録済み、本文へは未反映)
- A2 target WPM(125〜130)が体感として適切か(音声試作は次回)
- Pause 0.8秒・Outroさらなる減衰(前回試作分、未反映のまま保持)
- いずれも完成音声への反映はまだ行っていない

## Source of Truth更新

[OPEN_ITEMS.md](OPEN_ITEMS.md)を更新した。特にOPEN-30は、前回誤って
「見出しを発話しない」ことを解決策として記録していたため、**訂正**した
(見出しは発話する。見出しテキストを本文に含めて生成する方式へ訂正)。

## 作成・変更ファイル

- 新規: `er003_output/crosslevel_audio_04/investigation/`以下(unified_kp_pronunciation/, in_one_line_grounded_fix/, in_one_line_b1_reference/)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)
- 既存の完成音声・共有凍結モジュールは無変更

## Git status / commit / push

音声ファイルは`.gitignore`により追跡対象外。調査結果JSON・レポート・
OPEN_ITEMS更新をcommit済み。**pushは実行していません。**
