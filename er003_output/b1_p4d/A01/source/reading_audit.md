# ER-003-B1-P4D 読み正規化監査
- Pattern A文字数: 277
- marker(目印)置換件数: 5(5であるべき)
- used form残存: {'shot on target': 0, 'take players off': 0, 'a narrow lead': 0, 'close the door to the final': 0, 'stoppage time': 0}

## 静的検証結果
- reconstruction_matches: True
- unconvertible_token_count: 0
- ascii_letter_count: 0
- arabic_numeral_count: 0
- kanji_count: 0
- katakana_letter_count: 0
- marker_hiragana_count: 5(5であるべき)
- sentence_count_matches: True(source=4, script=4)
- punctuation_sequence_matches: True
- **all_passed: True**

## 重点表現(TTS前、期待変換結果)
- 最後の数分 → さいごのすうふん: present=True
- 守備を固め → しゅびをかため: present=True, forbidden(しゅびをかためる)present=False
- わずかなリード → わずかなりーど: present=True

## source hashes
```json
{
  "pattern_a_source_path": "er003_output/b1_p2/A01/listening_preview_raw.md",
  "pattern_a_source_sha256": "5b986705e6a55163bcc6cb6ab92a2d3a6be1970ab1b8c7adebd67ba2732aa500",
  "pattern_a_text_sha256": "0ed84df5a30ed7dd50c4027bfdb266364ae3668f4207a9e30a671369fc5db27e",
  "pattern_a_char_count": 277,
  "pattern_a_with_markers_sha256": "a28f3cf892fce482d27b5c512be1a260ca305c286c7f6625fd68aff9a4193cd8",
  "pattern_a_full_hiragana_sha256": "fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b"
}
```
