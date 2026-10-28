# Contributing to Copymunk

Thanks for helping make Copymunk better. Bug reports, translations and pull requests are all welcome.

## Before you start

- For anything bigger than a small fix, open an issue first so we can agree on the approach before you spend time on it.
- Copymunk has no third-party dependencies. Please keep it that way unless we have discussed it in an issue.

## Contributor License Agreement

Before your first pull request can be merged, you need to sign the [Contributor License Agreement](CLA.md). A bot will comment on the pull request with instructions: reply with the sentence it gives you, and you are done. You only sign once, and it covers all your future contributions.

**Why a CLA?** Copymunk is released under the [GNU GPLv3](LICENSE), and it is also distributed through the Mac App Store and the iOS App Store. Apple's terms add restrictions that the GPL does not allow, so the project can only keep shipping there if the maintainer holds the necessary rights to every line of code. The CLA grants those rights. You keep the copyright to your work, and the project stays open source under the GPLv3.

## Building and testing

See [Building from source](README.md#building-from-source) in the README. Pull requests run the CI workflow, which builds the Mac and iOS apps without signing and runs the `CopyoCore` unit tests. Please make sure it passes.

## Pull requests

- Keep each pull request focused on one change.
- Commit messages follow `[type][copyo][version]: summary`, where `type` is one of `feat`, `fix`, `docs`, `chore` or `refactor`, and the summary is a lowercase sentence in English. For example: `[fix][copyo][1.3.1]: show the iPad shortcut bar only with a hardware keyboard`.
- User-facing strings go through `Localizable.xcstrings`. If you add a string, add the English source text; translations for the other languages are welcome but not required.

## License

By contributing, you agree that your contributions are licensed under the GNU GPLv3 and under the terms of the [CLA](CLA.md).
