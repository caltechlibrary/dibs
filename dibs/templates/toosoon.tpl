<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('static/banner.html')
  <head>
    %include('static/standard-inclusions.html')
    <title>Cannot borrow this item at this time</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('static/navbar.html')

      <div class="container pt-3">
        <h4 class="alert-heading">Too soon</h4>
        <p id="with-barcode">We request that you wait at least an hour before
          borrowing the same item again.  Please try again after
          {{nexttime.strftime("%I:%M %p on %Y-%m-%d")}}.</p>
      </div>

      %include('static/footer.html')
    </div>
  </body>
</html>
