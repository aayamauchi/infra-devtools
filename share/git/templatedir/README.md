# git templatedir

This directory contains git templates which can be used to override
the default templates, including git hooks.

## Installation

1. clone the infra-devtools repository,

    `git clone git@bitbucket.org:redbookplatform/infra-devtools.git <DEVTOOLS_PATH>`

2. optionally use the hooks in one (or more) of the following ways:

    * Always use the latest pulled infra-devtools hooks:

      * Globally, overriding every repo's hooks:

        `git config --global core.hooksPath <DEVTOOLS_PATH>/share/git/templatedir/hooks`

      * In a single repo:

        `git config core.hooksPath <DEVTOOLS_PATH>/share/git/templatedir/hooks`

    * Copy the hooks when a new repo is cloned or init'd:

      * Copy from the latest pulled infra-devtools hooks:

          * Globally, for every repo:

            `git config --global init.templatedir <DEVTOOLS_PATH>/share/git/templatedir/hooks`

          * For just the current repo, enabling re-init of the repo:

            `git config init.templatedir <DEVTOOLS_PATH>/share/git/templatedir/hooks`

      * Copy later from a copy of the infra-devtool hooks made right now:

          1. `mkdir -p ~/.config/git/templatedir/hooks`
          2. `for f in <DEVTOOLS_PATH>/share/git/templatedir/hooks/* ; do
               cp ${f} ~/.config/git/templatedir/hooks/${f##*/}
              done`
          3. * Globally, for every repo:

                `git config --global init.templatedir ~/.config/git/templatedir/hooks`

              * For just the current repo, enabling re-init of the repo:

                `git config init.templatedir ~/.config/git/templatedir/hooks`

    * Copy the current infra-devtools hooks to the single repository:

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
