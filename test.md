# aws auth as str

```json
[{"error": "cannot compose AWS signing credentials"}]
```

{
    "auth": {
        "aws": {
            "accesskeyidenvvar": "AWS_ACCESS_KEY_ID",
            "credentialsenvvar": "AWS_SECRET_ACCESS_KEY",
            "type": "aws_signing_v4"
        }
    },
    "bin_path": "/home/javen/.local/stackql",
    "params": [
        "exec",
        "SELECT instanceState, COUNT(*) as num_instances FROM aws.ec2.instances WHERE region = 'ap-southeast-2' GROUP BY instanceState",
        "--auth",
        "{\"aws\": {\"credentialsenvvar\": \"AWS_SECRET_ACCESS_KEY\", \"accesskeyidenvvar\": \"AWS_ACCESS_KEY_ID\", \"type\": \"aws_signing_v4\"}}",
        "--output",
        "json"
    ],
    "parse_json": true,
    "platform": "Linux",
    "sha": "ce58a3b",
    "version": "v0.3.265"
}
# aws auth as dict

```json
[{"error": "cannot compose AWS signing credentials"}]
```

```
{
    "auth": {
        "aws": {
            "accesskeyidenvvar": "AWS_ACCESS_KEY_ID",
            "credentialsenvvar": "AWS_SECRET_ACCESS_KEY",
            "type": "aws_signing_v4"
        }
    },
    "bin_path": "/home/javen/.local/stackql",
    "params": [
        "exec",
        "SELECT instanceState, COUNT(*) as num_instances FROM aws.ec2.instances WHERE region = 'ap-southeast-2' GROUP BY instanceState",
        "--auth",
        "{\"aws\": {\"credentialsenvvar\": \"AWS_SECRET_ACCESS_KEY\", \"accesskeyidenvvar\": \"AWS_ACCESS_KEY_ID\", \"type\": \"aws_signing_v4\"}}",
        "--output",
        "json"
    ],
    "parse_json": true,
    "platform": "Linux",
    "sha": "ce58a3b",
    "version": "v0.3.265"
}
```

