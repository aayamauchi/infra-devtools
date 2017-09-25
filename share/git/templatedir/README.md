# git templatedir

This directory contains git templates which can be used to override
the default templates, including git hooks.

## Installation

1. Clone the infra-devtools repository:

    `git clone git@bitbucket.org:redbookplatform/infra-devtools.git <DEVTOOLS_PATH>`

2. Optionally use the hooks in one (or more) of the following ways:

    * Always use all of the latest pulled infra-devtools hooks:

        * Globally, overriding all hooks in every repo without a local core.hooksPath:

            `git config --global core.hooksPath <DEVTOOLS_PATH>/share/git/templatedir/hooks`

        * Locally, in the current repo:

            `git config core.hooksPath <DEVTOOLS_PATH>/share/git/templatedir/hooks`

    * Always use some of the latest pulled infra-devtools hooks:

        * Globally, for every repo:

            1. `mkdir -p ~/.config/git/templatedir/hooks`
            2. `ln -snf <DEVTOOLS_PATH>/share/git/templatedir/hooks/<HOOK_NAME> ~/.config/git/templatedir/hooks/`
            3. Repeat previous step for each desired hook
            4. `git config --global core.hooksPath ~/.config/git/templatedir/hooks`

        * Locally, in a single repo:

            1. `ln -snf <DEVTOOLS_PATH>/share/git/templatedir/hooks/<HOOK_NAME> <SINGLE_REPO_PATH>/.git/hooks/`
            2. Repeat previous step for each desired hook

    * Copy the hooks when a new repo is cloned or init'd:

        * Copy from the latest pulled infra-devtools hooks:

            * Globally, for every repo:

                `git config --global init.templatedir <DEVTOOLS_PATH>/share/git/templatedir/hooks`

            * Locally, in the current repo, enabling re-init of the repo:

                `git config init.templatedir <DEVTOOLS_PATH>/share/git/templatedir/hooks`

        * Copy later from a copy of the infra-devtools hooks made right now:

            1. `mkdir -p ~/.config/git/templatedir/hooks`
            2. `for f in <DEVTOOLS_PATH>/share/git/templatedir/hooks/* ; do
                 cp ${f} ~/.config/git/templatedir/hooks/${f##*/}
                done`
            3. Optionally, delete some hooks copied in the previous step
            4. * Globally, for every repo:

                    `git config --global init.templatedir ~/.config/git/templatedir/hooks`

                * Locally, in the current repo, enabling re-init of the repo:

                    `git config init.templatedir ~/.config/git/templatedir/hooks`

    * Copy the current infra-devtools hooks to a single repository:

        `cp <DEVTOOLS_PATH>/share/git/templatedir/hooks/* <SINGLE_REPO_PATH>/.git/hooks/`


## Notes

### pre-commit

This hook requires [YAMLLint](https://yamllint.readthedocs.io/) and will
abort commits that contain invalid YAML syntax.

### prepare-commit-msg

A very useful setting (for vi/vim users) when using the prepare-commit-msg
hook is the following:

`export GIT_EDITOR='vim +normal\ \$ -c startinsert!'`

With this setting in the environment, git will go to the end of the first
line of the commit message and open in edit mode.  Adding this to a
bashrc makes it the default for the terminal session.
