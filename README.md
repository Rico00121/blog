## For myself to remind commands
### Add post
```hugo new post/directoryName/index.md ```
### Start in local
```hugo server```
### Start in local with drafts
```hugo server -D```
### Publish the site
```hugo```

### Theme

The active theme is [Typo](https://github.com/tomfran/typo), vendored in
`themes/typo` from upstream commit `1b3db752a3989a9f43a2da52db4f183110d30295`.
The previous Anatole submodule is retained as a rollback option.

Site-level overrides in `layouts/` and `assets/` provide multilingual
navigation, compact social icons, CJK typography, localized controls, and
responsive post lists. The vendored theme also contains small compatibility
patches for Hugo 0.124 image rendering and GitHub Pages subpath font URLs.
