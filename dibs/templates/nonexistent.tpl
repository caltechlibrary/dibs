<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>No such item</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container pt-3">
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
