# Looking up one word

`get_latin_forms(word, pos=None)` takes a vocab-list entry and returns every
form of the dictionary word it names, one dict per form and grammatical slot.

```python
from omnes_formae import Frequency, PartOfSpeech, get_latin_forms

rows = get_latin_forms("amo, amare, amavi, amatum", "verb")
rows[0]["word"]   # 'amo'
rows[0]["tag"]    # 'present active indicative 1st person singular'

five_letter = {r["word"] for r in rows if len(r["word"]) == 5}
common_only = [r for r in rows if r["form_frequency"] == Frequency.MOST_COMMON]
```

**`word`** is the entry as a textbook writes it: `"amo, amare, amavi,
amatum"`, `"femina, -ae, f."`, `"in (+ abl.)"`, or just `"amo"`. Its first
Latin word must be the word's citation form, the form a dictionary lists it
under (the nominative, or a verb's 1st person singular present). The other
spelled-out words help choose among homographs: `"os, oris"` is "mouth", not
"bone". Case, macrons, *i*/*j* and *u*/*v* don't matter.

**`pos`** is optional: English words (`"noun"`, `"adjective, cardinal"`), a
`PartOfSpeech`, or its code (`"V"`). Without it, every part of speech is
searched, so a bare `"liber"` returns "children", "free" and "book".

It returns the root's forms, not every word the spelling could be a form of:
`"amor"` is the noun, not the passive of *amo*. When more than one word fits,
all of them come back, rare ones too, and each row says which word it is
from; filter the rows as you need. Words whose forms are all the same (*caelum*
"heaven" and "chisel") come back once, with both meanings. An empty list
means nothing matched, or the entry is an enclitic or prefix (`"-que"`).

The data loads on the first call (under a second); after that each call
takes about a millisecond, so looking up a whole vocab list is quick.

## The keys of each row

| Key | Example | Meaning |
|---|---|---|
| `word` | `"amabat"` | the form |
| `root` | `"amo, amare, amavi, amatum"` | the `word` argument, as given |
| `lemma` | `"amo, amare, amavi, amatus"` | Whitaker's dictionary heading for the word |
| `meaning` | `"love, like; ..."` | Whitaker's English; merged homographs' meanings are joined with `" \| "` |
| `pos` | `PartOfSpeech.VERB` | the form's part of speech (participles are `PARTICIPLE` under a verb) |
| `tag` | `"imperfect active indicative 3rd person singular"` | every grammar category of the form, in a fixed order; the same slot has the same tag in every word |
| `case`, `number`, `gender`, `tense`, `voice`, `mood`, `person`, `comparison`, `sort` | `"imperfect"` | the parts of the tag, each present only when it applies |
| `lemma_frequency` | `Frequency.MOST_COMMON` | how common the word is |
| `form_frequency` | `Frequency.MOST_COMMON` | how common this spelling of the form is |
| `form_age` | `Age.ANY` | when the form was in use |
| `entry_id`, `entry_ids` | `2871`, `[2871]` | the word's line in `DICTLINE.GEN` (negative: in `UNIQUES.LAT`); stable only while the data files are |

`PartOfSpeech`, `Frequency` and `Age` are Whitaker's own codes, with readable
names. Each member is also its code as a string, so `row["pos"] == "V"` is
true and JSON output shows `"V"`.

| `Frequency` | Code | For a word | For a form |
|---|---|---|---|
| `MOST_COMMON` | A | in every elementary Latin book | the usual form |
| `FREQUENT` | B | top 10 percent | a not unusual variant |
| `COMMON` | C | top 10,000 words | occasionally seen |
| `LESSER` | D | top 20,000 words | unlikely |
| `UNCOMMON` | E | 2 or 3 citations | rare |
| `VERY_RARE` | F | one citation | very rare |
| `INSCRIPTION_ONLY`, `GRAFFITI`, `PLINY_ONLY`, `UNKNOWN` | I, M, N, X | | |

`Age` runs `ARCHAIC` (A), `EARLY` (B), `CLASSICAL` (C), `LATE` (D), `LATER`
(E), `MEDIEVAL` (F), `SCHOLAR` (G), `MODERN` (H), with `ANY` (X) for forms
used throughout. See [Limitations](limitations.md) for what the lookup gets wrong.


---

AI disclosure: written with an AI assistant (Claude, by Anthropic), directed
and reviewed by [njg4ne](https://github.com/njg4ne).
