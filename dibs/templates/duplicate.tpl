<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Duplicate item</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container-fluid">
        <div class="alert alert-danger my-3" role="alert">
          <h4 class="alert-heading">Duplicate item</h4>
          <p id="with-barcode">An item with barcode {{barcode}} already exists in DIBS.</p>
        </div>
      </div>

      %include('common/footer.html')
      </div>
  </body>
</html>
