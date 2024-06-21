These tests aren't very regularly run - they're mainly designed to troubleshoot issues you may be having with data collection.

If you *are* having issues with various components, check this list:

- Make sure that the `AutofossGator` class isn't erroring during packet processing - all errors are silenced and can cause no data to come through
- Make sure that the `AutofossScale` class is exiting correctly and setting the `thread_running` attribute correctly - the main thread waits for this attribute to be `False` before exiting

If you're still having issues, shoot me a message on Slack. I'm always happy to help troubleshoot issues.
