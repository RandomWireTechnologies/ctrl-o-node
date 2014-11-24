# Ctrl-O Config File

# Copy this to config.py and then update the values to your secret values

# Hash secret is used to add uniqueness to the way a new hash is generated.
hashSecret = "Add your secret here"

# The local mysql database running on the Pi
localDBHost = "localhost"
localDBUser = "root"
localDBPass = "YourDBSecretPassword"
localDBDatabase = "member_web"

# The central mysql database which is used to update logs
remoteDBHost = "myname.ctrl-o.us"
remoteDBUser = "root"
remoteDBPass = "YourDBSecretPassword"
remoteDBDatabase = "member_web"