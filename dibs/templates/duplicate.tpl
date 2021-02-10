<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Duplicate item</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container-fluid main-container">
        <div class="alert alert-danger my-3" role="alert">
          <h4 class="alert-heading">Duplicate item</h4>
          <p id="with-barcode">An item with barcode {{barcode}} already exists in DIBS.</p>
        </div>
      </div>

      %include('common/footer.tpl')
      </div>
  </body>
</html>
