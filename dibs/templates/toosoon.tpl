<!DOCTYPE html>
<html lang="en">
  <!--
  Thank you for using
     ______          __  __                 __         ____    ____  ____   _____
    / ____/ ____ _  / / / /_  ___   _____  / /_       / __ \  /  _/ / __ ) / ___/
   / /     / __ `/ / / / __/ / _ \ / ___/ / __ \     / / / /  / /  / __  | \__ \ 
  / /___  / /_/ / / / / /_  /  __// /__  / / / /    / /_/ / _/ /  / /_/ /  __/ / 
  \____/  \__,_/ /_/  \__/  \___/ \___/ /_/ /_/    /_____/ /___/ /_____/ /____/  
  
  Please help us to improve this system by reporting problems using the
  GitHub issue system at https://github.com/caltechlibrary/dibs/issues
  or over email at helpdesk@library.caltech.edu
  -->                           
  <head>
    <title>Cannot borrow this item at this time</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  </head>
  
  <body>
    <div class="container-fluid">
      <div class="alert alert-warning my-3" role="alert">
        <h4 class="alert-heading">Too soon</h4>
        <p id="with-barcode">We request that you wait at least an hour before borrowing
        the same item again.  Please try again after {{nexttime.strftime("%I:%M %p on %Y-%m-%d")}}.</p>
      </div>
    </div
  </body>
</html>
