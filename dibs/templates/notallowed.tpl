<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Access error</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Access error</h4>
          <p>The requested method does not exist or you do not have permission
            to access the requested item.</p>
        </div>
      </div>

      %include('common/footer.html')
    </div>
  </body>
</html>
