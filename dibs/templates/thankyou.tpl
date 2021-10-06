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
          If you experienced any problems or have any suggestions for
          this service, please let us know!
          %if feedback_url:
          You can use our easy <a href="{{feedback_url}}">
          <nobr>feedback form</nobr></a>.
          %end
        </p>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
