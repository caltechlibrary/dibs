<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Too many loans</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Only one loan at a time</h4>
          <p>We regret that our policy currently prevents users from having
            more than one loan at a time.</p>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
