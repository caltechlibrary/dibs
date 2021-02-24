<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Error</title>
  </head>

  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container">
        <div class="alert alert-danger my-3" role="alert">
          <h4 class="alert-heading">Error: {{summary}}</h4>
          <p id="with-barcode">{{message}}</p>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
