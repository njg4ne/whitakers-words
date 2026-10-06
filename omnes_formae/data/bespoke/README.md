# Bespoke data

Data written for this project, not part of Whitaker's Words. The lookup
(`get_latin_forms`) reads it; the forms list doesn't.

- `labels.json`: the English word for each of Whitaker's grammar codes, used
  to build each form's tag ("NOM" -> "nominative"). The tags are meant to stay
  the same between versions, since people choose forms by them, so change a
  label only on purpose. `gender_abbreviation` is used in dictionary headings
  ("femina, feminae, f.").
- `pos_words.json`: the English part-of-speech words a vocab list may use, and
  the Whitaker codes (`PartOfSpeech` values) each one means. A word mapped to
  an empty list, like "enclitic", is known but has no dictionary words.
