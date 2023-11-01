# Vault Backup

This project is a backup solution that can help you to back automatically up your precious data and store it locally or remotely in an encrypted archive.

By default, the backup will be done only if there were made changes since "last_run" or if "force" is set to True.


## Usage

You just have to fill in the data in config.json, provide needed input arguments and launch the application.


## Json Structure


- **BOOL VALUE:** 
  - int: 0 or 1
  - string: "no"/"false" or "yes"/"true"
  - boolean: false or true
- **PASSWORD:**
  - must be base64 encoded
  - if provided as plain text, please enclose it in **"enc()"** or **"encrypt()"**
- **DATE:** timestamp in iso format or null
- **USERNAME, IP, PORT, ARCHIVE_NAME, PATH, LABEL, PATH_TO_STORAGE**: must be strings
- **VERSIONS**: must be int

Note: SSH is optional if there are no remote destinations.

	{
		"force": <BOOL VALUE>,
		"ssh": {
			"user": <USERNAME>,
			"password": <PASSWORD>,
			"ip": <IP>,
			"port": <PORT>
		},
		"backup": [
			{
				"name": <ARCHIVE_NAME>,
				"path": <PATH>,
				"password": <PASSWORD>,
				"destination": [
					{
						"label": <LABEL>,
						"path": <PATH_TO_STORAGE>,
						"remote": <BOOL VALUE>,
						"versions": <VERSIONS>,
						"last_run": <DATE or null>
					},
					...
				]				
			},
			...
		]
	}

## Input Arguments

There are 3 input arguments available: **"force", "password", "password_ssh"**.

The accepted format to provide these arguments is: **-Dargname='value'** or **-Dargname=value**

The same rules as for json values are applied here.
