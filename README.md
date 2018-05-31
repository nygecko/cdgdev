# cdgdev
Tech demo repository built with Python/HTML5/CherryPy/MongoDB.  
Initial implementation on Mac but easily modified for Windows.
Users can enter new demos into database via web UI or can upload multiple demos listed in a CSV-formatted document. 
Users can search for demos using keywords via web UI or can download all of them into a CSV-formatted document.
Demo Details Per Record:
  - Date Added
  - Name or Title
  - Description or High-Level Summary
  - Key Marketing Messages
  - Relevant Business Units
  - Technologies Incorporated
  - Demo Development Status [IDEA, WIP, DONE]
  - Event Usage (where has demo been shown?)
  - Owner/Contact Name
  - Links to Further Demo Content (videos, installs, etc.)
  - Notes/Misc Comments
  ## Getting Started
  - Install Python (built on 3.6.5) https://www.python.org/
  - Install CherryPy (built on 14.0.1) https://cherrypy.org/
  - Install PyMongo (built on 3.6.1) https://api.mongodb.com/python/current/
  - Download or clone CDGDEV repository
  ### Prerequisites
  Mac OS machine (portable to Windows with a few file I/O changes)
  Install Python and packages listed above
  ### Installing
  Initial Install
  1) Download and run Python package install: https://www.python.org/ftp/python/3.6.5/python-3.6.5-macosx10.6.pkg
  2) Open terminal window
  3) Enter command: cd ~
  3) Enter command: pip3 install virtualenv
  4) Enter command: pip3 install virtualenvwrapper
  5) Enter command: virtualenv chypy
  6) Enter command: cd chypy
  7) Enter command: source bin/activate
  8) Enter command: pip install cherrypy
  9) Enter command: python -m pip install pymongo
  Open Dev Environment
  1) Open terminal window
  2) Enter command: mongod <start MongoDB service>
  3) Open new terminal window
  4) Enter command: source ~/chypy/bin/activate
  5) Enter command: cd <CDGDEV directory>
  6) Enter command: python cdgdev.py 
  7) Open browser window and navigate to http://127.0.0.1:8080
  8) Login as Admin for full functionality
  ## Testing
  ...
  ## Deployment
  ...
  ## Built With
  Python (built on 3.6.5) https://www.python.org/
  CherryPy (built on 14.0.1) https://cherrypy.org/
  PyMongo (built on 3.6.1) https://api.mongodb.com/python/current/
  ## Contributing
  ...
  ## Versioning
  ...
  ## Authors
  Nygecko
  ## License
  This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
  ## Acknowledgments
  ...
  
