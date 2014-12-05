# Ctrl-O Config File

# Copy this to config.py and then update the values to your secret values

# Hash secret is used to add uniqueness to the way a new hash is generated.
hashSecret = "Add your secret here"

# The local mysql database running on the Pi
localDBHost = "localhost"
localDBUser = "ctrl-o"
localDBPass = "ctrl-o-db-password"
localDBDatabase = "ctrl-o"

# The central mysql database which is used to update logs
remoteDBHost = "you.randomwire.biz"
remoteDBUser = "ctrl-o"
remoteDBPass = "ctrl-o-db-password"
remoteDBDatabase = "ctrl-o"
remoteDBPort = 6779
remoteDBSSL = {'ca':'/etc/mysql/ca-cert.pem'}