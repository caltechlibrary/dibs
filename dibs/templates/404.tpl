<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Error</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 4em; min-height: 100%">
      %include('common/navbar.tpl')

      <div class="container text-center">
        <img src="{{base_url}}/static/missing.jpg" class="rounded img-fluid pt-3" style="max-width: 500px" width="80%"
             title="Photo taken in the Sherman Fairchild Library in January, 2021. Copyright 2021 Rebecca Minarez. Distributed under a CC BY-NC-SA 4.0 license."
             alt="Photo of missing books by Rebecca Minjarez, Caltech.">
        <h4 class="my-4">Very sorry, but that seems to be missing &#8230;</h4>
        <p class="mx-auto" style="width: 85%">We hate when that happens! 
          Maybe it's been misplaced, or maybe it's really gone. Our
        staff will take note of the missing item. Our apologies for the
        inconvenience.</p>

        <p class="text-muted"><small>(Code {{code}}: {{message}})</small></p>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
