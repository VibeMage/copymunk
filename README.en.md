# Copymunk

[简体中文](README.md)

Copymunk is an open-source clipboard manager for Mac, iPhone and iPad. On the Mac it lives in the menu bar, `⇧⌘V` brings up a floating card panel, and you search your history as you type.
On iPhone and iPad you browse and search what you copied on your Mac through your own iCloud, and save new clips as you go. Website: [copymunk.com](https://copymunk.com)

On the Mac, data stays on this Mac by default (`~/Library/Application Support/Copyo/`) and syncing is off by default; there are no third-party SDKs, no analytics and no crash reporting, which makes it a fit for workplaces that do not allow third-party closed-source tools.

## Features

### Mac

- **Clipboard history**: records what you copy in the background — plain text, rich text, links, colors (`#RRGGBB`), images, files
- **Floating panel**: press `⇧⌘V` and a glass panel floats up above the Dock, showing your history as a horizontal flow of cards, each tinted with its source app’s color
- **Search as you type**: once the panel is open, just start typing to filter; searches content, file names and the source app
- **Keyboard first**: `← →` to navigate, `⇥` to switch filters, `↩` to copy and return to the previous app, `⇧↩` to copy as plain text, `⌘1–9` to copy the Nth card, `Space` to preview, `⌘P` to pin, `⌘⌫` to delete, `Esc` to close
- **Pinboards**: pin the clips you use often into groups of your own; history-limit cleanup never touches them
- **Source app badge**: each card shows a kind badge, the source app's icon and “source · time”; color clips are tinted with the color itself
- **Drag and drop**: drag a card straight out into any app
- **Privacy**: content that password managers and the like mark as Concealed/Transient is skipped automatically; you can also ignore specific apps by bundle ID
- **Sync (optional, pick one of three)**: Off / Folder / iCloud. The folder option writes your history and Pinboards out as snapshots into iCloud Drive
  or any directory all of your devices can read and write (a company NAS, another cloud-sync folder, and so on), and **does not propagate deletions** — an entry you delete on one Mac
  stays on your other Macs. The iCloud option syncs through your own iCloud private database, where additions, edits and deletions all take effect, so **a deletion disappears from every device at once**.
  Either way the data only ever passes through storage you own. Sync is off by default, so Copymunk can stay completely offline in a corporate environment
- **Custom shortcut**: `⇧⌘V` by default; record any key combination in Settings
- **History limit**: 100/300/500/1000/unlimited; past the limit, the oldest unpinned entries are cleaned up automatically
- **Launch at login**, hiding the menu bar icon, pausing capture, plain-text mode and other settings
- **Eight languages**: English, Simplified and Traditional Chinese, French, German, Spanish, Japanese and Arabic (laid out right to left), following the system language, built on a String Catalog

### iPhone and iPad

iOS doesn't let apps read the clipboard in the background, so on iPhone and iPad Copymunk saves at moments you choose:

- **Synced with your Mac**: iCloud Sync is on by default; choose iCloud in the Mac's sync settings and what you copy there shows up on your phone
- **Saves when you open it**: every time you open or return to Copymunk it reads the clipboard and saves anything new (you can turn this off and use the system Paste button instead)
- **Share sheet**: select text, a link or an image in any app and share it to Copymunk, optionally straight into a Pinboard
- **Quick Save**: press and hold the Action Button, tap the Control Center or Lock Screen control, or use Back Tap
- **Widgets and Shortcuts**: a Recent Clips widget for the Home Screen, and "Save Clipboard" in Shortcuts and Siri
- **Cards**: tap to copy, swipe right to pin, swipe left to delete, touch and hold for more
- **iPad**: sidebar and card grid, drag cards into other apps, and hardware keyboard shortcuts

## Installation

- **Mac, iPhone and iPad**: the [App Store](https://apps.apple.com/app/id6813955206), free, one listing for all three. The Mac needs macOS 14 or later, iPhone and iPad need iOS / iPadOS 18 or later
- **Mac direct download**: [download the DMG](https://github.com/VibeMage/copymunk/releases/latest/download/Copymunk.dmg) (every version is on [Releases](https://github.com/VibeMage/copymunk/releases)), open it and drag Copymunk
into Applications. Official releases are signed with a Developer ID and notarized by Apple, so a double-click is all it takes —
you only get the standard "app downloaded from the Internet" confirmation dialog the first time.

## Building from source

Requires Xcode 16+ and macOS 14+.

```bash
git clone https://github.com/VibeMage/copymunk.git && cd copymunk
xcodebuild -project Copyo.xcodeproj -scheme Copyo -configuration Release -derivedDataPath build build
open build/Build/Products/Release/Copymunk.app   # or copy it to /Applications
```

You can also just open `Copyo.xcodeproj` in Xcode and run it (⌘R).

### Running the latest build day to day (maintainers)

```bash
./scripts/install-local.sh   # build Release → replace /Applications/Copyo.app → relaunch
```

It installs the direct-distribution flavor (not sandboxed), which reads your everyday history in
`~/Library/Application Support/Copyo/`, signed with your Apple Development certificate so iCloud sync works
(requires your team account in Xcode). The previous version is kept in `build.noindex/install/previous/`.
If `/Applications` holds the App Store version, the script stops first; delete that copy and run it again.
It only quits the `/Applications` copy of Copymunk and leaves other instances such as Debug builds running,
just listing them (they compete with the new install for ⇧⌘V).
Only the `/Applications` copy stays registered: builds live under `build.noindex/` (skipped by Spotlight)
and are unregistered from LaunchServices after installing, so “Open With” doesn’t fill up with dev builds.
Test App Store builds through TestFlight.

The iOS / iPadOS app lives in the same project (scheme `Copyo iOS`, iOS 18+, sharing `CopyoCore` and the iCloud data with the Mac app). To build it for the simulator:

```bash
xcodebuild -project Copyo.xcodeproj -scheme "Copyo iOS" -configuration Debug \
  -destination 'generic/platform=iOS Simulator' -derivedDataPath build CODE_SIGNING_ALLOWED=NO build
```

The project uses Xcode's automatic signing, with the maintainer's Team filled in. Contributors should switch the Team
to their own under Signing & Capabilities in Xcode, or pass it in at build time:

```bash
xcodebuild -project Copyo.xcodeproj -scheme Copyo -configuration Release \
  -derivedDataPath build DEVELOPMENT_TEAM=<your-team-id> build
```

If you only want to compile and take a look, with no plans to install it on another machine, add `CODE_SIGNING_ALLOWED=NO` to skip signing entirely.
Note that iCloud sync depends on an iCloud container and the push capability on the App ID, so it is unavailable when you build with your own Team
(you would need to create an iCloud container in your own developer account and change `CopyoStore.cloudKitContainerIdentifier`).
Everything else works as usual.

## Packaging for distribution (maintainers)

```bash
EXPORT_PROFILE="Copymunk Developer ID" NOTARIZE=1 ./scripts/build-release.sh
# archive → export with this Mac's Developer ID certificate and provisioning profile
# → Apple notarization → staple → produces dist/Copymunk-<version>.dmg + .zip
```

Sign-in and notarization both use the App Store Connect API key (shared with `scripts/asc.rb`, kept in `~/.appstoreconnect/`, never in the repository),
so you don't need an Apple ID signed in to Xcode or an app-specific password; the comments at the top of the script cover the options and the profile.
When uploading to Releases, add a copy of the DMG named `Copymunk.dmg` next to the versioned DMG / ZIP and `SHA256SUMS.txt`:
the website's download button always points at `releases/latest/download/Copymunk.dmg`.

- The script needs a Developer ID certificate and the matching provisioning profile (including the iCloud container and the push capability).
  **Without a developer certificate** (when building from source yourself, say): just build with `CODE_SIGNING_ALLOWED=NO` as described
  above. The result is only good for your own machine; on any other machine macOS says the app "is damaged and can't be opened"
  (Gatekeeper's boilerplate for apps with no developer identity), which one run of `xattr -cr /Applications/Copymunk.app` clears.
- In a corporate environment with MDM (Jamf and friends), you can distribute it through an allowlist instead.

### Updating

Official releases always carry the same signing identity, so installing a new DMG over the old version (drag it into Applications and replace) is all you need.
Your history lives in `~/Library/Application Support/Copyo/` and is left untouched.

## Icon

The icon's source lives in `art/app-icon-exploration/2026-10-15-copymunk-final/`, with the spec in
`copymunk-icon-spec.md` there. The 10 macOS sizes (16 and 32 are hand-tuned optical drafts), the iOS
light / dark / tinted variants and the two menu bar templates are all rendered straight from their own
SVGs by one script, then synced into the asset catalogs:

```bash
python3 art/app-icon-exploration/2026-10-15-copymunk-final/render.py   # re-render from the SVGs in sources/
./scripts/make-icon.sh            # copy the 15 PNGs into the three asset catalogs
./scripts/make-icon.sh --check    # only compare the asset catalogs with the source
```

`render.py` needs Pillow and resvg-py (`python3 -m pip install --user Pillow resvg-py`);
`make-icon.sh` only copies and never rescales, so small sizes and iOS variants are never blurred by downscaling.

Then rebuild to pick it up.

## Keyboard shortcuts

| Action | Shortcut |
| --- | --- |
| Open / close the panel | `⇧⌘V` (global, customizable in Settings) |
| Move between cards | `←` `→` |
| Copy the selection and return to the previous app | `↩` or double-click the card |
| Copy as plain text | `⇧↩` (the 1.1-era `⌥↩` still works in 1.2 and goes away in the next release) |
| Copy the Nth card | `⌘1`–`⌘9` |
| Cycle filters | `⇥` / `⇧⇥` |
| Preview the selection | `Space` (when the search field is empty; while typing it inserts a space) or `⌘Y` |
| Pin to a Pinboard / unpin | `⌘P` |
| Search | just start typing |
| Close the preview / clear the search / close the panel | `Esc` |

## Architecture

The project's targets: `Copyo/` is the Mac app, `CopyoIOS/` the iPhone / iPad app, `CopyoShareExtension/` the share extension,
`CopyoWidgets/` the widgets and Control Center control, `CopyoShared/` code shared by the iOS targets, and `CopyoCore/` the Swift
Package both platforms share (data model and storage). The Mac app is laid out like this:

```
Copyo/
├── App/        app entry point, menu-bar residency (NSStatusItem)
├── Models/     SwiftData models: ClipItem, Pinboard
├── Services/   clipboard polling, writing back to the clipboard and returning focus to the previous app, global hotkey, iCloud sync, icon color extraction, thumbnail cache
├── Panel/      the floating panel (NSPanel + SwiftUI): card flow, search, filters, the preview child window and the “Copied” toast
└── Settings/   Settings window (General / Sync / Shortcuts / History / About)
```

Implementation notes:

- macOS has no notification API for clipboard changes, so `ClipboardMonitor` polls `NSPasteboard.changeCount` every 0.3s (what every clipboard tool does)
- Text wins over images when capturing: apps like Excel and Numbers put an image rendering on the clipboard alongside the text you copied, so the entry has to be recorded as text
- The global hotkey uses Carbon `RegisterEventHotKey`, with zero third-party dependencies; the app does not use the Accessibility permission
- Storage is SwiftData (SQLite); images go through `externalStorage` plus SHA-256 deduplication and a thumbnail cache
- Sync has two mutually exclusive channels: the folder option merges snapshots (iCloud Drive or any shared directory works,
  no paid developer account needed, but deletions are not propagated); the iCloud option has SwiftData mirror straight into the CloudKit
  private database, syncing additions, edits and deletions in full. Both use the same `Copyo.store`, and only one is ever active at a time

## License

[GPL-3.0](LICENSE)
