<!DOCTYPE html>
<html lang="en">
  %include('static/banner.html')
  <head>
    <title>Error</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  </head>
  
  <body>
    <div class="container-fluid">
      <div class="alert alert-danger my-3" role="alert">
        <h4 class="alert-heading">Error</h4>
        <p id="with-barcode">{{message}}</p>
      </div>
    </div
  </body>
</html>
