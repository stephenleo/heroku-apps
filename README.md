# name-gender

Mono-repo deployment
- Follow documentation from here: 
    1. https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-multi-procfile
    2. https://elements.heroku.com/buildpacks/lstoll/heroku-buildpack-monorepo

- Add the following buildpacks:
    ```
    heroku buildpacks:add -a <app> https://github.com/lstoll/heroku-buildpack-monorepo -i 1

    ```
- Add the following 
    ```
    APP_BASE=relative/path/to/app/root

    ```
- Push each app
    ```
    git push git@heroku.com:<app> main
    ```
- Add python buildpack: `heroku buildpacks:add -a name-gender-backend heroku/python`
- Test locally: `heroku local web`
- Deploy: 
- For each git push, push to the heroku remote which was changed first. if it works then push to github
- check logs: `heroku logs --tail`
