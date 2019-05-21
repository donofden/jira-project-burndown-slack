[![HitCount](http://hits.dwyl.io/donofden/jira-project-burndown-slack.svg)](http://hits.dwyl.io/donofden/jira-project-burndown-slack)

# jira-project-burndown-slack
CLI script to retrieving data from Azure DevOps

This script will fetch the current iteration of a given team and get the workitems to calculate the story points availabe in the columns. This can be used to know the burndown of a team in a daily basis.

## Configuration

You will need the update the variables in Makefile:

```
JIRA_TOKEN
```
Kindly check the document of [JIRA API](https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/)

[Check here for more information, on how to get the above details](https://developer.atlassian.com/server/jira/platform/rest-apis/)

To generate **JIRA_TOKEN** [Follow the link here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html)

The arguments can be passed via the Makefile:
```
Calculate burn down for the Day from JIRA Scrum Board

optional arguments:
  -h, --help            show this help message and exit
  -a TOKEN, --token TOKEN
                        Authorization Token to JIRA Board
```
## Result

```apacheconfig
=============  =======  ========
..               items    points
=============  =======  ========
Done                 4        22
Ready To Test        1         8
In Progress          1         8
Code Review          1         2
TOTAL                7        40
=============  =======  ========
```

## Integrating with Slack & Jenkins

![Full screen](doc/screen-7.png)

This script can be run via Jenkins and Post result to the slack channel, to reduce the time to check it manaually and the rest of the team can view the burndown daily. An agile team can use it as they are self-organizing team.

Create a Pipeline Project in Jenkins with the following configurations:

![Full screen](doc/screen-1.png)

Since we need to pass the ID we need to create add this credentials in Jenkins si it can be passed dynamically.

`This project is parameterized` - we are going to create one `String Parameter` & three `Credentials Parameter`.

![Full screen](doc/screen-5.png)

We are using `Jenkins Credentials Provider: Jenkins` to secure our Token and ID's generated from ADO.

![Full screen](doc/screen-6.png)

To run `Pipeline` we use `Pipeline script`

```
node('linux') {
    def date = new Date()
    String datePart = date.format("dd-MM-yyyy")
    String timePart = date.format("HH:mm")
    
    withCredentials([
        string(credentialsId: 'JENKINS_CREDENTIALS_PROVIDER_ID_PROJECTID', variable: 'P1'),
        string(credentialsId: 'JENKINS_CREDENTIALS_PROVIDER_ID_TEAMID', variable: 'P2'),
        string(credentialsId: 'JENKINS_CREDENTIALS_PROVIDER_ID_ADO_TOKEN', variable: 'P3'),
    ]) {
            git([url: 'git@github.com:ado-project-burndown-slack.git', branch: 'master'])
            def getResult
            
            
            stage ('Execute Script') {
              getResult = sh(
                script: "python daily-burn-down.py -g "+GROUPID+" -p "+'${P1}'+" -t "+'${P2}'+" -a "+'${P3}'+"",
                returnStdout: true,
              )
            }
            stage ('Send Slack Notification') {
              slackSend channel: '#your-slack-channel-name', color: 'good', message: '```' +getResult+ '``` Burndown '+datePart+'  '+timePart+' :white_check_mark:'
            }
        }
    }
```

Please note that I haven't covered the integration of `Send Slack Notification` you can [check for more information here..](https://jenkins.io/doc/pipeline/steps/slack/)


