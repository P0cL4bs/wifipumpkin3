# Contributing to wifipumpkin3

We want to make contributing to this project as easy and transparent as possible.You can help this project by reporting problems, suggestions, locating it or contributing to the code.

### Report a problem or suggestion

Go to our [issue](https://github.com/P0cL4bs/wifipumpkin3/issue) and check if your problem / suggestion has already been reported. Otherwise, create a new issue with a descriptive title and detail your suggestion or steps to reproduce the issue.
A good bug report should not let others need to chase you for more
training. Please try to be as detailed as possible in your report.

### Repository
This repository has some features in order to facilitate the organization of work.

#### Branchs
The branches are distributed in:

- master - Stable version. Something will only be added to this branch when it is really relevant for the release of a new version.

- beta - Stable version that contains most of the major features, but is not yet complete.relevant to the launch of a new beta version on release.

- dev - Unstable version. It is the continuous version of development. All approved and tested modifications will be added to this branch.

- inbox - Branch for receiving Pulls Requests. All pulls must be directed to this branch, which, if approved, will be merged into the dev.

- draft - Draft branch, used when testing new features and pulls.

- news - Branch containing the current functionality under development by the maintainer.

## Contribution with code

#### Getting Started

When developing wp3, follow these steps to setup your environment, format your code, and run app and unit tests:

if you want to develop a new feature, use a unit testing framework to create unit tests, run them, and report the results of these tests. i recommend frist create a unit tests `test_features.py` into directory `tests`.

1. Fork [wifipumpkin3][] on Github.

2. Clone the git repo:
```bash
$ git clone https://github.com/$USERNAME/wifipumpkin3
$ cd wifipumpkin3
```

3. Setup the virtual environment with dependencies and tools, follow the steps to install the tool.

4. Format your code using [*Black*](https://github.com/ambv/black):
```bash
$ make format
```

## Pull Requests

We actively welcome your pull requests. Send the pull requests on branch `inbox` and now wait the answer.

1. If you've added code that should be tested, add unit tests.
2. update the documentation if necessary.
3. Ensure the test suite passes if you add a new unit tests.

## Issues

We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

## License

By contributing to Wp3, you agree that your contributions will be licensed
under the `LICENSE` file in the root directory of this source tree.