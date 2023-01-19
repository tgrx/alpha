# Rebranding

If you're using this project as a template, you definitely want it to have your brand insted of "Alpha".
There is a tool in AMT which may help you.

Run `python -m alpha.management rebranding --help` to know details.

It automates renaming/removing of some parts of the project, but some items can be refactored only manually.

## Manual refactoring

### Github CI

1. [.github/workflows/deploy-dockerhub.yml](https://github.com/tgrx/alpha/blob/main/.github/workflows/deploy-dockerhub.yml)

    This job will not run for you at all.

    This job can be run only by [@tgrx](https://github.com/tgrx). So you need to change this first. 

    Then, it requires `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD` to be set
    in [repo's secret settings](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).
    They are required because image is published to [alexandersidorov/alpha](https://hub.docker.com/r/alexandersidorov/alpha/).
    Hence, you need to set a proper credentials.
    
    And this will not help either! You need to change the Docker Hub repo to yours!

    So, there are 3 points to be changed to make this job work.
    Since they are quite sensitive, no automation provided for this.

1. [.github/workflows/deploy-heroku.yml](https://github.com/tgrx/alpha/blob/main/.github/workflows/deploy-heroku.yml)

