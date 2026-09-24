# mk270 vs ben-crowell forks

Two forks are compared here:

- `submodules/mk270` is Martin Keegan's cleanup of Whitaker's Ada source, hosted on GitHub.
- `submodules/ben-crowell` is Ben Crowell's 2024 fork of mk270, hosted on Bitbucket.

The forks split at `9b11477` (2023-02-23). Since then mk270 has 46 commits and was last
active in Aug 2026. ben-crowell has 39 commits and was last active in Apr 2026.

The notes below come from reading the source, the history and the CI configs. Neither fork
has been built locally yet.

## Closer to the original

**ben-crowell, narrowly.**

- **Data:** its `INFLECTS.LAT`, `DICTLINE.GEN` and `UNIQUES.LAT` are still Whitaker's.
  mk270 changed them for issue #101 (Greek 2nd-declension `2 7` forms), plus a whitespace
  fix in `DICTLINE.GEN`. The three files differ by about 90 lines in total.
- **Behavior:** ben-crowell does change the default behavior, and mk270 doesn't. It strips
  macrons, turns off the "MORE" pause, sets the screen size to 50, and adds the
  `WHITAKER_USER` / `WHITAKER_DEV` environment variables.
- **Lineage:** mk270 is still the main upstream. ben-crowell forked because mk270 went quiet,
  and mk270 has since picked back up.

## Works better

**mk270 for correctness, ben-crowell for scripting.**

- **mk270:** has fixes from 2026 for new GNAT versions (paren and old-style qualification
  warnings) and CRLF handling. It also fixes a `-que` tackon bug and adds a test for it
  (`test/05_multusque`), and it includes the issue-101 inflection fixes. CI runs build and
  test on every push, plus Linux and Windows binary builds.
- **ben-crowell:** has fixes from 2024–25 for GNAT bitrot and has repaired the
  `dictpage`/`uniqpage` tools. It also has the macron stripping, environment-variable config
  and no pager listed above, which help when shelling out to it. It has a `make install`
  target, but it hard-codes `/lib`, `/bin` and `/usr/share`.

## Easier to build in Podman

**About the same; mk270 is slightly safer.**

- **Same build:** both need only `gnat gprbuild make` from Debian/Ubuntu apt, then `make`.
- **mk270:** its CI (`.github/workflows/ci.yml`) is exactly that recipe running on
  `ubuntu-latest`, so it has been shown to work on a current toolchain.
- **Keeping it cheap:** use a multi-stage build. Compile in a `debian:stable-slim` image with
  GNAT installed, then copy `bin/words` and the data files (`*.GEN`, `*.LAT`, `INFLECTS.SEC`)
  into a slim runtime image. The GNAT toolchain is the big layer, and the runtime doesn't need
  it.

## For generating paradigms (all forms of *amo* / *mater*, with filters)

**Use mk270's data files. Neither fork can generate paradigms itself.**

- **Neither generates paradigms:** both forks only parse (form → lemma). A generator would be
  new code, most easily a small Python tool. It would read `DICTLINE.GEN` for the stems and
  the declension or conjugation class, then read `INFLECTS.LAT` for the tagged endings, and
  filter on those tags.
- **mk270's data is more correct:** its `INFLECTS.LAT` includes the issue-101 fixes, and those
  files are the input that matters here.
- **Checking the output:** feed the generated forms back into a built `words` binary to confirm
  that each one parses to the expected lemma. ben-crowell's no-pager default and environment
  variables make that step easier to script, but mk270 works with a `WORD.MOD` file too.
