# HR_TITLE_NOTE_01(委任_09、2026-10-25。API 0、Lock解除・回避・再生成なし)

## 1. 試聴URL(Human Review用・完成候補ではない・noindex)
https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_02/hr_title/index.html
(題 3 attempt + Advanced組立済みの参考mp3。公開差替えではない)

## 2. attempt別の転写・判定理由
題(台本)=「月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密」(`run_ms_03/entry_point.json` japanese_title)。証跡=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/audit/review_lock_state.json`、`a2/narration/attempts/japanese_title_attempt{1,2,3}_*.{wav,json}`。

| attempt | 経路 | 主ASR(OpenAI)転写 | 副ASR(Azure)転写 | 判定 |
|---|---|---|---|---|
| 1 | 標準(custom) | 月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。 | 未実施 | NG_PROTECTED / p1_value_diff(8,900本→8000・800本) |
| 2 | 標準(custom) | 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | NG_BOTH / secondary_not_accepted(数値は主・副とも一致=EQUAL。『しわ』が死/詩と転写され不採用) |
| 3 | minimal_fallback | 月の氏は8000900本超。その奥に潜む岩の上着の秘密。 | 未実施 | NG_PROTECTED / p1_value_diff |

観察: 全attemptで『しわ』が詩/死/氏と転写されているが、ASRの綴りは読みの根拠にならない(同音語)。attempt2は副ASRが『8900本』と正しく転写しており、数値の読み自体は正しい可能性が高い。聴くポイント=「8,900本超」の読み(はっせんきゅうひゃっぽんちょう)と『しわ』『岩の上着』の読み。

## 3. HR承認後の再開手順(Fable権限。人間の聴取結果を受けてFableが実行。今回は実行していない)
(a) 承認(Lock→REGENERATE_APPROVED。次の1回のみ再生成許可。`er011_human_review_lock_01.py:474` approve_regenerate):
```
.venv/Scripts/python.exe -c "import er011_human_review_lock_01 as h; print(h.approve_regenerate('er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/japanese_title.wav', text='<TTS入力の題テキスト(canonical_text_sha256=b02b1f60...と同一のもの)>', approved_by='user'))"
```
(b) 該当segmentのみTTS(1起動。再起動は委任文が許可した回数のみ):
```
.venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug moon_shrinking --run run_ms_03 --level a2 --stage tts --only-segments japanese_title
```
(c) 組立・player:
```
.venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug moon_shrinking --run run_ms_03 --level a2 --stage assemble
.venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug moon_shrinking --run run_ms_03 --level a2 --stage player
```
注: 委任文の`--stages provision_shell,gate,assemble,pages,page_verify`はZ runner(`er026_family_z_fiction_production_runner_01.py`)の段指定で、Xのer019 runnerの`--stage`には存在しない(choices=plan/scaffold/study_text/tts/assemble/player/all、er019:2764)。X用の公開ページ生成は別途(共通builder経由)必要で、再開時にFableが段を確定する。また承認(a)は音声が正しいと人間が判断した場合は「承認=現状wavを正として確定」する別経路(既存wavをOKとして記録)が適切な可能性があり、再生成するか確定するかは人間聴取後の判断。
費用: 再生成する場合は題1segmentのTTS+ASR=約0〜数円(題segment 1回あたり1円未満が実績水準)。確定のみなら0円。

## 4. 事実の整理
「8,900本超」は欄(E: reader_must_hear_number)の外にある中核数値で、Writer規則5では許可された中核数値であり、O-2'は同単位系(m)のみを対象とするため、別単位系の補足数値として題に使われた(検証済み設計どおりの挙動)。題に数値を載せること自体は仕様違反ではなく、問題は音声ASR判定が数字+「本」の読みを転写で安定して確認できなかった点にある。
