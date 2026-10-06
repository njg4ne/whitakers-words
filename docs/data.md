# From a lemma to every form: how the WORDS data fits

The goal: given a starter such as *ago*, *agere*, *mater* or *matris*, list every form of the
word with its grammar, in the way *amabantur* is one form of *amo* (imperfect passive
indicative, 3rd plural). Then filter that list.

> **Btw, what's a lemma?** A *lemma* is the headword you'd look a word up under in a
> dictionary. It stands for every inflected form of that word. Latin dictionaries cite a
> lemma by its *principal parts*, the few forms you need to derive all the others:
>
> - **Nouns:** nominative and genitive singular plus gender. *mater, matris* f. The genitive
>   shows the declension and the stem the other cases are built on (`matr-`).
> - **Verbs:** usually four principal parts. *ago, agere, egi, actus*, which are the present
>   1st singular, present infinitive, perfect 1st singular, and perfect passive participle.
>   Each one supplies a stem for a group of tenses (`ag-`, `ag-`, `eg-`, `act-`).
>
> So *amabantur* is a form, and *amo, amare, amavi, amatus* is its lemma. Going from a form to
> its lemma is called *lemmatization*, which is what WORDS does. Going from a lemma to all its
> forms (its *paradigm*) is what we want. WORDS's `DICTLINE.GEN` stores each lemma as exactly
> these principal-part stems.

Three plain-text files in either fork hold everything needed:

| File | Role | Size |
|---|---|---|
| `DICTLINE.GEN` | The lexicon: each word's stems, its declension or conjugation, and its meaning | ~39,000 lines |
| `INFLECTS.LAT` | Every ending, tagged with its grammar and the stem it attaches to | ~1,800 entries |
| `UNIQUES.LAT` | Irregular forms that can't be built from a stem plus an ending | 79 records |

The core idea: **form = stem (from `DICTLINE`) + ending (from `INFLECTS`)**. The parser in
WORDS runs this backwards. It strips an ending, then looks up what's left as a stem. A
generator runs it forwards.

Everything below comes from the files and the Ada source in `submodules/mk270`.
ben-crowell's copy differs in only a few lines of data (see `compare.md`).

## `DICTLINE.GEN`: one line per dictionary entry

Each line uses fixed columns. Columns 1–76 hold four stem slots, each 19 characters wide. From
column 77 on, the fields are separated by spaces: the part of speech and its class codes, then
five one-letter flags (age, area, geography, frequency, source), then the English meaning.

```
ag                 ag                 eg                 act                V      3 1 X            X X X A O drive/urge/conduct/act; ...
am                 am                 amav               amat               V      1 1 X            X X X A O love, like; ...
mater              matr                                                     N      3 1 F T          X X X A X mother, foster mother; ...
sequ               sequ               zzz                secut              V      3 1 DEP          X X X A O follow; ...
```

**What the stem slots mean** (called the "stem key" in `INFLECTS`):

| Key | Noun (`N`) | Verb (`V`) |
|---|---|---|
| 1 | Nominative singular stem: `mater` | Present stem, as in the 1st singular: `ag` → *ago* |
| 2 | Stem for the other cases: `matr` → *matris* | Present stem, as in the infinitive: `ag` → *agere* |
| 3 | — | Perfect stem: `eg` → *egi* |
| 4 | — | Participle and supine stem: `act` → *actus* |

**The class codes:**
- **Nouns** (`N 3 1 F T`): declension `3`, variant `1`, gender `F`, and a kind (`T` = thing).
- **Verbs** (`V 3 1 X`): conjugation `3`, variant `1`, and a kind: `X` for ordinary verbs,
  or `TRANS`, `DEP` (deponent), `IMPERS`, `TO_BEING` (compounds of *sum*), and so on.
  The kind changes which forms exist. For example, a deponent has no active finite forms.
- **`zzz`** marks a stem that doesn't exist. For example, *sequor* has no perfect stem
  because its perfect is *secutus sum*. Skip any ending that needs a `zzz` stem.

## `INFLECTS.LAT`: one line per ending

```
N     3 0 GEN S X  2 2 is        X A
V     1 1 IMPF  PASSIVE IND  3 P  1 7 abantur       X A
V     0 0 PERF  ACTIVE  IND  3 S  3 2 it            X A
VPAR  0 0 NOM S M PERF PASSIVE PPL 4 2 us           X A
```

The fields, reading left to right:
1. Part of speech.
2. Declension or conjugation, then variant.
3. The grammar. For nouns: case, number, gender. For verbs: tense, voice, mood, person,
   number. For participles (`VPAR`): case, number, gender, tense, voice, `PPL`.
4. The stem key (1–4).
5. The ending's length, then the ending. A length of `0` means the bare stem.
6. Age and frequency flags.

**Matching rules.** These come from the `"<="` operators in
`src/latin_utils/latin_utils-inflections_package.adb`. An ending applies to a word when all of
these hold:

- **Class:** the ending's class and variant match the word's exactly, or the ending has the
  same class with variant `0` (it applies to every variant), or the ending is `0 0` (it
  applies to every class except 9).
  - Example: `N 3 0` endings apply to every 3rd-declension noun.
  - Example: `V 0 0 PERF` endings apply to every conjugation, because all perfects inflect
    alike.
- **Gender:** the genders are equal, or the ending's gender is `X` (any), or it is `C` (common)
  and the word is `M` or `F`.
- **Other tags:** `X` in tense, voice, mood and similar fields is a wildcard.

## Worked examples

**amo → *amabantur*.** The `DICTLINE` entry is `am / am / amav / amat`, `V 1 1`. It matches
this ending:

```
V     1 1 IMPF  PASSIVE IND  3 P  1 7 abantur
```

The ending uses stem 1, which is `am`, so `am` + `abantur` = ***amabantur***: imperfect
passive indicative, 3rd plural.

**mater.** The entry is `mater / matr`, `N 3 1 F`. It matches:

| `INFLECTS` line | Why it matches | Result |
|---|---|---|
| `N 3 0 NOM S X 1 0` | Variant 0, gender X | stem 1 + nothing = *mater* |
| `N 3 0 GEN S X 2 2 is` | Variant 0, gender X | `matr` + `is` = *matris* |
| `N 3 1 ACC S C 2 2 em` | Exact class, and C covers F | *matrem* |
| `N 3 0 ABL P X 2 4 ibus` | Variant 0, gender X | *matribus* |

**ago.** The entry is `ag / ag / eg / act`, `V 3 1`. It matches:

| `INFLECTS` line | Result |
|---|---|
| `V 3 0 PRES ACTIVE IND 1 S 1 1 o` | *ago* |
| `V 3 1 PRES ACTIVE INF 0 X 2 3 ere` | *agere* |
| `V 0 0 PERF ACTIVE IND 3 S 3 2 it` | *egit* |
| `VPAR 0 0 NOM S M PERF PASSIVE PPL 4 2 us` | *actus* |

## Starting from any form (*agere*, *matris*)

A user might type a form that isn't the dictionary headword. To find the entry, run the
matching backwards, the way the WORDS parser does:

1. For each `INFLECTS` ending the input ends with, strip it.
2. Look up what's left in `DICTLINE`, in the stem slot that ending names.
3. Keep the entries whose class passes the matching rules above.

For example, *matris* − `is` (stem key 2) = `matr`. That's slot 2 of `mater / matr` (`N 3 1`),
and `N 3 0 GEN S` is compatible, so the input is *mater*. The same steps turn *agere* into
`ag` in slot 2 of `V 3 1`, which is *ago*.

A form can match more than one entry. For example, `fer` is the stem of a noun, an adjective
and *fero*. The tool should list the candidates, or accept a part-of-speech hint.

The other option is to shell out to a built `words` binary, which does exactly this lookup.
That needs the Ada build (see `compare.md`).

## What the data doesn't cover: rules that live in the Ada code

- **Compound tenses.** `INFLECTS` has no perfect passive endings, because those tenses are two
  words: the perfect participle plus a form of *sum* (*actus est*, *amati erant*). The parser
  recognizes these combinations in `src/words_engine/words_engine-parse.adb` ("PERF PASSIVE
  PPL + esse"). A generator has to build them itself, from the participle forms and the
  paradigm of *sum*.
- **Verb kinds.** `DEP`, `SEMIDEP`, `IMPERS` and similar kinds restrict which voices and persons
  exist. The generator has to apply those restrictions.
- **Irregulars.** Irregular verbs are partly handled with special classes and variants:
  - `V 5 1` with kind `TO_BEING` is *sum* and its compounds (*absum*, *adsum*).
  - `V 6 1` is *eo*, with stems `e / i / iv / it`.
  - `V 6 2` is *volo*.
  - `V 3 2` is *fero*, with stems `fer / fer / tul / lat`.

  They are also partly handled by `UNIQUES.LAT`, which stores fully spelled forms in three-line
  records:

  ```
  agatur
  V      3 1 PRES PASSIVE SUB 3 S  IMPERS             F  X  X  E  E
  let it be treated; let it be a matter or question of;
  ```

  Each record carries the full grammar tags but no stem, so linking one to its `DICTLINE`
  entry takes matching on class and meaning.
- **Spelling variants.** The parser's "tricks" (i/j, u/v, medieval spellings) and the tackons
  in `ADDONS.LAT` (*-que*, *-ne*) are for recognizing forms. A paradigm generator doesn't
  need them.

## Filtering

Every generated form carries the tags from its `INFLECTS` line, so filters are plain equality
checks:

- **Nouns:** case, number, gender.
- **Verbs:** tense, voice, mood, person, number.
- **Participles:** case, number, gender, tense, voice.

The age and frequency flags can drop variants the user may not want. For example, the poetic
1st-declension genitive in *-ai* is marked `B B`. Keeping only frequency `A` gives the
textbook paradigm.

---

AI disclosure: written with an AI assistant (Claude, by Anthropic), directed
and reviewed by [njg4ne](https://github.com/njg4ne).
