<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Too many loans</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Only one loan at a time</h4>
          <p>We regret that our policy currently prevents users from having
            more than one loan at a time.</p>
        </div>
      </div>

      %include('common/footer.html')
    </div>
  </body>
</html>
