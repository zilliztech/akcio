We extend a warm invitation to contribute to Akcio by submitting issues, responding to queries, enhancing documentation, and sharing code. Irrespective of the nature of your contribution, we request you to practice professionalism and respectfulness.

## Submitting issues

If you have found a bug or have a feature request, please [submit an issue](https://github.com/zilliztech/akcio/issues) on our GitHub repository.
Here are some guidelines to follow when submitting an issue:

1. Check if the issue has already been reported. If it has, you can add your input by commenting on the issue.

2. Provide a clear and concise description of the issue you are experiencing.

3. Include any relevant details such as error messages, steps to reproduce the issue, and the version of Akcio you are using.

4. If possible, provide a code snippet that can help us reproduce the issue.


## Improving documentation

Good documentation is essential for any project, and Akcio is no exception.
The Akcio documentation contains both **READMEs** and **[Wiki pages](https://github.com/zilliztech/akcio/wiki)**.
If you see an area of the documentation that can be improved, please feel free to submit a pull request with your changes.

## Contributing to modules

You are welcome to share customized methods for each module:

- **agent**: sharing prompt templates, building a new agent, etc.
- **embedding**: using a different tool or service
- **llm**: adding a new model or service
- **store**: enabling more configurations, integrating with other databases, etc.
- **data loader**: cutomizing splitter, processing documents with additional steps, etc.

To ensure seamless integration of a new module into the system, adherence to the [Customization Guides](https://github.com/zilliztech/akcio/wiki#customization) is recommended.



## Pull requests

We follow a fork-and-pull model for all contributions. Before starting, we strongly recommend looking through existing PRs so you can get a feel for things.

If you're interested in contributing to the `zilliztech/akcio` codebase, follow these steps:

1. Fork [Akcio](https://github.com/zilliztech/akcio). If you've forked Akcio already, simply fetch the latest changes from upstream.

2. Clone your forked version of Towhee.

    ```bash
    $ git clone https://github.com/<your_username>/akcio.git
    $ cd akcio
    ```
    
    If you've done this step before, make sure you're on the `master` branch and sync your changes.

    ```bash
    $ git checkout master
    $ git pull origin master
    ```

3. Think up a suitable name for your update, bugfix, or feature. Try to avoid using branch names you've already used in the past.

    ```bash
    $ git checkout -b my-creative-branch-name
    ```

4. During development, you might want to run `pylint`. You can do so with one of the commands below:
    ```bash
    $ pip install pylint==2.10.2
    $ pylint --rcfile=.pylintrc --output-format=colorized src.towhee
    $ pylint --rcfile=.pylintrc --output-format=colorized src.langchain
    $ pylint --rcfile=.pylintrc --output-format=colorized offline_tools
    ```

6. Submit your pull request on Github. Folks in the community will discuss your pull request, and maintainers might ask you for some changes. This happens very frequently (including maintainers themselves), so don't worry if it happens to you as well.

    > Please ensure that the first line of your PR is as follows:
    >
    > Signed-off-by: Your Name your.email@domain.com


Thank you for your interest in contributing to Akcio. We appreciate all contributions and look forward to working with you!
