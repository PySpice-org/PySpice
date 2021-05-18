# PySpice Portal

## File Structure

Pelican Third Parties
* `pelican-plugins`
* `pelican-themes`

Pelican Setup
* `pelicanconf.py`
* `publishconf.py`
* `tasks.py`

Pelican Output: `output`

Theme: `theme`
* `theme/template/index.html`
* `theme/template/src => /src`

Content:
* `content/pages`

## Build Pelican

```
inv -l
```

## Build Theme

```
yarm install
```

```
yarn add  ...
yarn -D add ...

yarn outdated

yarn upgrade-interactive
yarn upgrade --latest
```

Build and serve portal
```
inv regenerate
# parallel
inv server
# parallel
npx gulp
```

```
inv livereload
# parallel
npx gulp build
```
