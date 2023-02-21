# basic instantiation
```
v0.3.265
```

```
{
    "bin_path": "/home/javen/.local/stackql",
    "params": [
        "exec",
        "--output",
        "json"
    ],
    "parse_json": true,
    "platform": "Linux",
    "sha": "ce58a3b",
    "version": "v0.3.265"
}
```

# upgrade stackql
```
v0.3.265
```

```
installing stackql...
downloading latest version of stackql from https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip to /home/javen/.local

Download complete.
stackql upgraded to version v0.3.265
```

```
v0.3.265
```

# output tests

## json output (default)

```json
[{"provider":"aws","version":"v23.01.00108"},{"provider":"azure","version":"v23.01.00104"},{"provider":"googleworkspace","version":"v23.01.00116"},{"provider":"k8s","version":"v23.01.00104"},{"provider":"netlify","version":"v23.01.00104"},{"provider":"okta","version":"v23.01.00104"},{"provider":"sumologic","version":"v23.01.00104"},{"provider":"youtube","version":"v23.01.00116"},{"provider":"azure_extras","version":"v23.01.00104"},{"provider":"firebase","version":"v23.01.00114"},{"provider":"github","version":"v23.02.00118"},{"provider":"google","version":"v23.01.00116"},{"provider":"googleads","version":"v23.01.00116"},{"provider":"googleanalytics","version":"v23.01.00116"},{"provider":"googledevelopers","version":"v23.01.00116"},{"provider":"googlemybusiness","version":"v23.01.00116"}]
```

## csv output with headers

```
provider,version
aws,v23.01.00108
azure,v23.01.00104
googleworkspace,v23.01.00116
k8s,v23.01.00104
netlify,v23.01.00104
okta,v23.01.00104
sumologic,v23.01.00104
youtube,v23.01.00116
azure_extras,v23.01.00104
firebase,v23.01.00114
github,v23.02.00118
google,v23.01.00116
googleads,v23.01.00116
googleanalytics,v23.01.00116
googledevelopers,v23.01.00116
googlemybusiness,v23.01.00116

```

## csv output without headers

```
aws,v23.01.00108
azure,v23.01.00104
googleworkspace,v23.01.00116
k8s,v23.01.00104
netlify,v23.01.00104
okta,v23.01.00104
sumologic,v23.01.00104
youtube,v23.01.00116
azure_extras,v23.01.00104
firebase,v23.01.00114
github,v23.02.00118
google,v23.01.00116
googleads,v23.01.00116
googleanalytics,v23.01.00116
googledevelopers,v23.01.00116
googlemybusiness,v23.01.00116

```

## table output

```
|------------------|--------------|
|     provider     |   version    |
|------------------|--------------|
| aws              | v23.01.00108 |
|------------------|--------------|
| azure            | v23.01.00104 |
|------------------|--------------|
| googleworkspace  | v23.01.00116 |
|------------------|--------------|
| k8s              | v23.01.00104 |
|------------------|--------------|
| netlify          | v23.01.00104 |
|------------------|--------------|
| okta             | v23.01.00104 |
|------------------|--------------|
| sumologic        | v23.01.00104 |
|------------------|--------------|
| youtube          | v23.01.00116 |
|------------------|--------------|
| azure_extras     | v23.01.00104 |
|------------------|--------------|
| firebase         | v23.01.00114 |
|------------------|--------------|
| github           | v23.02.00118 |
|------------------|--------------|
| google           | v23.01.00116 |
|------------------|--------------|
| googleads        | v23.01.00116 |
|------------------|--------------|
| googleanalytics  | v23.01.00116 |
|------------------|--------------|
| googledevelopers | v23.01.00116 |
|------------------|--------------|
| googlemybusiness | v23.01.00116 |
|------------------|--------------|

```

## text output

```
provider,version
aws,v23.01.00108
azure,v23.01.00104
googleworkspace,v23.01.00116
k8s,v23.01.00104
netlify,v23.01.00104
okta,v23.01.00104
sumologic,v23.01.00104
youtube,v23.01.00116
azure_extras,v23.01.00104
firebase,v23.01.00114
github,v23.02.00118
google,v23.01.00116
googleads,v23.01.00116
googleanalytics,v23.01.00116
googledevelopers,v23.01.00116
googlemybusiness,v23.01.00116

```

