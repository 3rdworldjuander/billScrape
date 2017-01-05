Working version
### PLIST  
+  invokes billScrape.py to run every 10am of everyth 10th of the month  

### billScrape.py  
+  checks AT&T site and parses individual subscriber's monthly bills.  
+  sends email with monthly bill.  
+  uses ConfigParser to separate login credentials and email lists from script. 
+  use hover before clicking after login to workaround website behaviour of returning to the overview page.   
+  output system hostname pragmatically. 
