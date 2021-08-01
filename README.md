# name-gender

## Deploying apps from a mono-repo on Heroku
- Check current heroku apps
    ```
    heroku apps
    ```
- Create a new heroku app for app in the mono-repo
    ```
    heroku create -a <app>
    ```
- Add the following buildpacks:
    ```
    heroku buildpacks:add -a <app> https://github.com/lstoll/heroku-buildpack-monorepo -i 1
    heroku buildpacks:add -a <app> heroku/python
    ```
- Add the following configs
    ```
    heroku config:set -a <app> PROCFILE=relative/path/to/app/Procfile
    heroku config:set -a <app> APP_BASE=relative/path/to/app
    ```
- Test locally
    ```
    heroku local web
    ```
- Push each app to heroku
    ```
    git push git@heroku.com:<app> main
    ```
- Check logs
    ```
    heroku logs --tail
    ```
- If everything works fine push to github
    ```
    git push origin main
    ```
- References:
    1. https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-multi-procfile
    2. https://elements.heroku.com/buildpacks/lstoll/heroku-buildpack-monorepo
