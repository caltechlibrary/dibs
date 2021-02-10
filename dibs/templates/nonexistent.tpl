<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>No such item</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">No such item</h4>
          %if barcode == 'None':
          <p id="without-barcode">This item does not exist.</p>
          %else:
          <p id="with-barcode">An item with barcode {{barcode}} does not exist.</p>
          %end
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
