<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('static/banner.html')
  <head>
    %include('static/standard-inclusions.html')
    <title>Access error</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('static/navbar.html')

      <div class="container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Access error</h4>
          <p>The requested method does not exist or you do not have permission
            to access the requested item.</p>
        </div>
      </div>

      %include('static/footer.html')
    </div>
  </body>
</html>
