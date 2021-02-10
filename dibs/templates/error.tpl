<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Error</title>
  </head>

  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container">
        <div class="alert alert-danger my-3" role="alert">
          <h4 class="alert-heading">Error</h4>
          <p id="with-barcode">{{message}}</p>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
