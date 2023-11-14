# Setup

```console
heroku create core-recommender
```

# Making chancog installable
I have already done what is need to install chancog from github during heroku deployment. Here are the steps I used.

Add a new class authorization token via the github website (Settings --> Developer Settings --> Personal access tokens)

Add this token to ENV variables in via the heroku website (Settings --> Config vars). The name is GITHUB_AUTH_TOKEN and the value is the token you just created.

Run the following command to use add the buildback that knows how to handle github authorizations.

```console
heroku buildpacks:add -i 1 https://github.com/heroku/heroku-buildpack-github-netrc.git
```

The active buildbacks are actually visible right below the Config vars on the heroku website (Settings --> Buildbacks).

To deploy, use the Deploy tab on the heroku website. I presently do manual deployments, which can be from any branch that has been pushed back to github.
