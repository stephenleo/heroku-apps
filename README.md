# Heroku Apps
- A mono-repo with all my heroku deployments. 
- Each deployment is a directory within `src/`

## Deployments
| Name                                     | Description                                         |
|------------------------------------------|-----------------------------------------------------|
| [BoyOrGirl]( https://www.boyorgirl.xyz ) | Check if your names are Boy's names or Girl's names |


## Deploying apps from a mono-repo on Heroku
- Check current heroku apps
    ```
    heroku apps
    ```
- Create a new heroku app for app in the mono-repo
    ```
    heroku create -a <app> --remote <app>
    ```
    - To update an existing app with a remote
        ```
        heroku git:remote -a <app> -r <app>
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
- If everything works fine push to github
    ```
    git push origin main
    ```
- Push each app to heroku
    ```
    git push https://git.heroku.com/<app>.git HEAD:main
    ```
- Check logs
    ```
    heroku logs --tail
    ```
- Setup Automatic Ping at [Kaffeine](https://kaffeine.herokuapp.com/)
- References:
    1. https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-multi-procfile
    2. https://elements.heroku.com/buildpacks/lstoll/heroku-buildpack-monorepo
