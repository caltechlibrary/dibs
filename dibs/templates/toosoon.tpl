<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Cannot borrow this item at this time</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container pt-3">
        <h4 class="alert-heading">Too soon</h4>
        <p id="with-barcode">We request that you wait at least an hour before
          borrowing the same item again.  Please try again after
          {{nexttime.strftime("%I:%M %p on %Y-%m-%d")}}.</p>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
