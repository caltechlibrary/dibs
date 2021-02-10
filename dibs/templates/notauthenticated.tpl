<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Access error</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container pt-3">
        <div class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Access error</h4>
          <p>Caltech DIBS is restricted to members of Caltech only.</p>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
