<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Thank you</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container pt-3">
        <h1 class="mx-auto text-center my-3 caltech-color">
          Thank you for using Caltech DIBS!
        </h1>
        <p class="mx-auto col-6 my-5 text-center text-info font-italic">
          If you have any comments or suggestions, please don't hesitate
          to let us know by using our <a href="{{feedback_url}}">
          anonymous feedback form</a>.
        </p>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
