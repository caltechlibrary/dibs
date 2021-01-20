<!DOCTYPE html>
<html lang="en">

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
