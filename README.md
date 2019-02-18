# issueflow <!-- omit in toc -->

The repo supports of the Chinese localizations for both Istio and Kubernetes repos. It uses Chatbot + Webhook to manage Github issues for tracking the work tasks, providing the smooth task management support.

- [Workflow](#workflow)
- [Tasks (Issues) state transition](#tasks-issues-state-transition)
- [How-to use slack bot](#how-to-use-slack-bot)
- [Runtime Config](#runtime-config)
	- [File layout](#file-layout)
	- [Config file](#config-file)
	- [Startup Script](#startup-script)
	- [Bot Command List](#bot-command-list)
- [How to use `Webhook`](#how-to-use-webhook)
	- [Configure file](#configure-file)
	- [Environment variables](#environment-variables)
	- [Github config](#github-config)

## Workflow

This project assumes the minimum efforts from the upstream organization,
which means it currently runs independently.

1. Create a github repository for managing the transaltion tasks.
2. Invite the translation team members to join the repository, and the tasks (which are github issues) are distributed within the project.
3. Initialize Chatbot and environment.
4. Use Chatbot to create tasks and refresh the tasks.
5. Initialize Webhook and its environment.
6. Link the repository webhook to the already-setup webhook
7. Translator use Github comment to start the translation flow and progress report.
8. Webhook would identify the github issue's comments and update issue labels accordingly.

Overall workflow：

![workflow](workflow.png)

## Tasks (Issues) state transition

Tasks are shown as Github Issue, and use label to reflect the task's current state.

> The following satte and commands are be configured in `Webhook`

- `Welcome` state: The newly created `Issue` would be labeled as `Welcome`,
Issue Body would contian the source file corresponding to this task,
It needs administrator to confirm to the next phase.
The confirmation can be done in two ways:
  - Github comment: `/confirm`.
  - Direct label update: Remove `Welcome`, add `Pending`.

- `Pending` state: In this state, translation team member can claim the task by using github comment `/accept`

- `Translating` state: After the claim, the task would be assigned to the team member and updated to this state.

- `Pushed` state: After the translation is complete, translator can move the task into state by using github comment, `/pushed`.

- `Finished` state: After the PR got merged, transaltor can close the task by using github comment, `/merged`.

## How-to use slack bot

## Runtime Config

### File layout

Create directory for Bot, the folders are:

- `config`: place to put the config file.
- `data`: Bot data.
- `repository`: Code repository, can be divided into multiple branches.

### Config file

Bot configure file is yaml snippet.
Below is the example that currently used in the Istio localization project:

~~~yaml
repositories:
  istio:
    github: # task repository information
      owner: servicemesher
      repository: istio-official-translation
    valid_extensions: # only track `.md` file changes for generating tasks
    - ".md"
    labels: # newly-created tasks, along with the following labels as default
    - priority/P0
    branches: # branch info, every branch will have its own checkout directory
    - name: "1.1" # name identifier, would be used in the ChatBot
      value: master
      path: "/errbot/repository/master" # container directory after mounted
      url_prefix: # prefix included in the created task
        source: "https://github.com/istio/istio.io/tree/master/content"
      labels: # default label for this branch when creating the task
      - version/1.1
    source: # source file and relative directory
      name: en
      path: content
    languages: # target file name and relative directory
    - name: zh
      path: content_zh
      labels: # default label for this localization task
      - lang/zh
~~~

### Startup Script

There are some needed configuration during the Bot startup:

~~~bash
#!/bin/sh
docker run -d --name=istio-slack-bot \
        --restart=always \
        -e BOT_LOG_LEVEL=INFO \
        -e BOT_ADMINS=@dustise \ # Administrator's slack name
        -e REPOSITORY="istio" \ # Repo name in the configure file
        -e REPOSITORY_CONFIG_FILE="/errbot/config/repository.yaml" \ # Config file directory
        -e MAX_RESULT=10 \ # Max output # of issues at a time
        -e MAX_WRITE=30 \ # Max issues at a time
        -e TARGET_LANG="zh" \ # Target translation language
        -e BOT_TOKEN="xoxb-" \ # Slack Bot's Token
        -e BACKEND="Slack" \ # Backend as Slack
        -e CRITICAL_COMMANDS="find_new_files_in,find_updated_files_in,cache_issue" \ # Critical command list
        -e OPERATORS="@dustise" \ # The administrator to execute the commands
        -e PRIVATE_COMMANDS="whatsnew,github_bind,github_whoami" \ # Commands can be used in DM
        -v $(pwd)/data:/errbot/data \ # Bot's storage directory
        -v $(pwd)/config:/errbot/config \ # Bot's configure directory
        -v $(pwd)/repository:/errbot/repository \ # Repository directory
        dustise/translat-chatbot:20190213-3 # Docker image name
~~~


### Bot Command List

After the startup, you can see the Bot App in Slack,
you can send commands to it and execute corresponding tasks.
The command prefix is `!`.

- `github bind [your github token]`: Bind your Github personal access token to the Bot so that the tasks would be executed under your identity.

- `github whoami`：Verify command, check if the Github token binding is working.

- `cache issue`：Cache all the open tasks.

- `find new files in [branch name]`： Check the to-be-translated tasks from the corresponding branch, `branch name` comes from the config file. If adding flag `--create_issue=1`, the bot would create tasks based on the newly-created files.

- `find updated files in [branch name]`：Idenfity the updated files which got updated after the last translation. The command flags are similar to the above one. The task creation batch is controlled via environment flag.

- `whatsnew`：Check the unassigned tasks.

- `show issue [issue id]`：Show the issue link by issue ID.

- `search issues [query]`：Use Github search syntax to search issues.

## How to use `Webhook`

Currently, `Webhook` only supports two deployment models, Flash App vs GCP Function.
Enter the corresponding directory and execute `xxx-build.sh` to do the package.

> GCP needs `permission.json` config file to write the logs. This needs customized configuration.

### Configure file

Current workflow is defined throughout YAML file.
Below if an example for Istio project

~~~yaml
workflow:
- name: "istio" # project name
  labels: # available labels
  - group: "status" # label groups, can be used for configuration based on the group
    labels:
      - "welcome"
      - "pending"
      - "translating"
      - "pushed"
      - "finished"
  events:
    on_issue: # Webhook 的触发动作。
    - name: "new_issue"
      description: "A new issue had been created."
      regex: opened # 触发的具体事件
      conditions: [] # conditions to execute action
      actions: # action list
      - type: label # label the github issue
        value:
          group: status # label's group
          label: welcome # label name
          mutex: True # exclusive
    on_comment:
    - name: "confirm"
      description: "Accept an new issue as a task."
      regex: \/confirm # `/confirm` command
      conditions:
      - type: labels
        value: # must contain the following labels
        - "welcome"
        failed_actions: # if failed to satisfy, then
        - type: comment # add github comment
          value: "Sorry @%operator%, only issues with label `welcome` can be confirmed." # github comment
      - type: state # issue state must be `open`
        value: "open"
        failed_actions:
        - type: comment
          value: "Sorry @%operator%, only active issues can be accepted."
      - type: assigned # unassigned task
        value: False
        failed_actions:
        - type: comment
          value: "Sorry @%operator%, only issues had not been assigned can be confirmed."
      - type: user_in_list # user in the administrator group
        value:
        - "%admin%"
        failed_actions:
        - type: comment
          value: "Sorry @%operator%, you are not allowed to confirm this issue."
      actions: # pass the check, add label `pending`
      - type: label
        value:
          group: status
          label: pending
          mutex: True
    ...
~~~

### Environment variables

- `GITHUB_TOKEN`：Github token to complete Issue operation.

- `ADMINS`：Github users name to execute the administrator commands.

- `INTERVAL`：Write operation interval to avoid the Github API rate limit.

- `WORKFLOW`：Workflow name in the configure file.

### Github config

Set task repository's Webhook as deployment address, and use `Issue`, `Issue_comment` to trigger the flow.
