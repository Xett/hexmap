# Shax
## Overview
Shax is a wrapper for the inbuilt python logging class. Shax implements the [HierarchicalObject](https://github.com/Xett/Gaap/wiki/HierarchicalObject) class from the [Gaap](https://github.com/Xett/Gaap) package.
## Importing
For the Logger to be used, an object must be passed in that conforms to Hierarchy specifications. That is, it contains 2 member variables; a string \_name and an object \_parent that also conforms to Hierarchy specifications. The LoggableObject class conforms to these specifications. 

When using, take care of the order of imports; LoggableObject inherits from a class that implements the Logger class. The following includes all 3 imports, in the correct order, though the second import is superfluous.
```python
from Shax import Logger
from Gaap import Hierarchy
from Shax import LoggableObject
```
## Usage
An object can inherit from the LoggableObject class. When doing so, take care not to call the Logger to log using the classes unset, future logger. 

By default, a root logger will be implemented, and LoggableObject takes care of adding a new logger.
```python
Logger().log(msg, logger, level=None)
```
If no logger is set, the root logger will be used instead.

If no level is set, it will be logged on whatever level the root logger is on.

The format of the logged message is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
## Logger Levels
Level|When it's used
-----|--------------
DEBUG|Detailed information, typically of interest only when diagnosing problems.  
INFO|Confirmation that things are working as expected.
WARNING|An indication that something unexpected happened, or indicative of some problem in the near future(e.g 'disk space low'). The software is still working as expected.
ERROR|Due to a more serious problem, the software has not been able to perform some function.
CRITICAL|A serious error, indicating that the program itself may be unable to continue running.
