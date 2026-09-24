---
name: verify-forms
description: Check word_form_enumerator output after a change - regenerate, compare against the previous output, spot-check known paradigms and known non-forms, and optionally validate against the Ada parser.
---

# Verify enumerator output

## 1. Regenerate and compare

```sh
S=$(mktemp -d)
git stash -q && python3 -m word_form_enumerator -o $S/before.txt; git stash pop -q
python3 -m word_form_enumerator -o $S/after.txt
wc -l $S/before.txt $S/after.txt
diff <(sort -u $S/before.txt) <(sort -u $S/after.txt) | head -50
```

Every added or removed form should be explainable by the change you made. The
baseline at data commit `1f2f0fb` is 1,399,668 lines and 1,185,893 unique.

## 2. Spot checks

Each of these must be present (`grep -cx WORD forms.txt` ≥ 1):

| Covers | Forms |
|---|---|
| 1st conj. | amo amabantur amabar amatus |
| 3rd conj. + perfect/participle | ago agere egit actus |
| 3rd decl. noun, two stems | mater matris matrem matribus |
| esse (synthesized entry) | sum es est fuit esse |
| sum compound (`V 5 1`, `TO_BEING`) | abes |
| deponent | sequor sequi secutus |
| irregular stems | tuli latus eo it |
| short imperatives | dic fer |
| PACK + tackon | quicumque cujuscumque quendam |
| impersonal (incl. kept infinitive) | oportet oportere |

Each of these must be **absent**:

| Why | Forms |
|---|---|
| Deponents have no active forms | sequo |
| Short imperatives only for dic/duc/fac/fer | ag (as the imperative of ago) |

```sh
for w in amo amabantur mater matris ago agere egit actus sum es fuit esse abes \
         sequor sequi secutus tuli dic fer quicumque cujuscumque quendam oportet; do
  grep -qx "$w" forms.txt || echo "MISSING $w"; done
for w in sequo ag; do grep -qx "$w" forms.txt && echo "UNEXPECTED $w"; done
```

`ag` can legitimately appear from other entries, so check which entry
produced it before worrying.

## 3. Ada parser as an oracle (not yet done; ask the user before building a container)

Build either fork: `apt-get install gnat gprbuild make && make` in a
`debian:stable-slim` Podman container, which is the same recipe as mk270's
`.github/workflows/ci.yml`. Then run a sample of forms through `bin/words`, one
per line, and collect the ones reported as `UNKNOWN`. Any unknown form is either
a generator bug or a deliberate deviation listed in `AGENTS.md`. Set
`WORD.MOD` / `WORD.MDV` (or, on ben-crowell, the `WHITAKER_USER` environment
variable) to turn off the pager and the tricks, so the output is easy to parse.
