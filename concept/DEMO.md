### Demo "Activation"
If we use Google Assistant we need to activate the App first
> U: Ok Google, activate Lara
>
> L: Hey, how can I help you?


### Demo "Context"
This dialog demos how Lara can remember context and behave accordingly.
Additionally it is demoing several features for issue management (list, filter, close, comment)

> U: How many issues are there assigned to me?
>
> L: There are 7 issues on 3 different projects assigned to you.
>
> U: And are there any new bugs?
>
> L: Two of your issues are labeled "bug" and are not older than three days. Do you want me to read them out?
>
> U: Yes
>
> L: Issue 1: 'Error message when starting'; Issue 2: 'Login broken on Internet Explorer 6'
>
> U: Close the second issue and write a comment saying: 'We do not support Browsers older than one year'


### Demo "What do I have to do today?"
Demos Laras ranking algorithm for Issues, Pull requests (and maybe calendar?)

> U: What do I have to do today? / What should I do next?
>
> L: ...


### Demo "Who can help me with...?"
This demo shows how Lara can semantically search through git histories and identify other people in the same organization that have a profession in a certain field

> U: Who can help me running project 'XY' in a Docker container?
>
> L: There are two people in your organization that worked with Docker in Python repositories lately: "Max Mustermann" and "John Doe".
>
> U: Great! ...