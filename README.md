# FileHTTPServer

This server is intended to serve only one selected file or directory as answer to all the requests.
To every request it starts a new thread.

Sending directories is realised with on the fly zip compression.

# Syntax

It's the same on files and directories.

```bash
FileHTTPServer.py /path/to/file
```

# Todos

* Limit the possible number of threads paralell threads.
* Cache zipped directory content to reduce the compression's performance requirement.
