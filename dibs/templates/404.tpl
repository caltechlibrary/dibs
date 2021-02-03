<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('static/banner.html')
  <head>
    <title>Error</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  </head>
  
  <body>
    <div style="position: relative; padding-bottom: 4em; min-height: 100%">
      <div class="container text-center">
        <img src="/static/missing.jpg" class="rounded img-fluid pt-3" style="max-width: 500px" width="80%"
             title="Photo taken in the Sherman Fairchild Library in January, 2021. Copyright 2021 Rebecca Minarez. Distributed under a CC BY-NC-SA 4.0 license."
             alt="Photo of missing books by Rebecca Minjarez, Caltech.">
        <h4 class="my-4">Very sorry, but that seems to be missing &#8230;</h4>
        <p class="mx-auto" style="width: 80%">Maybe it's somewhere else, or
        maybe it's really gone. We hate when that happens! We like to keep
        things organized, because &#8230; well, we're a library, you
        know? Anyway, our staff will take note of the missing item. Our
        apologies for the inconvenience.</p>

        <p class="text-muted"><small>(Code {{code}}: {{message}})</small></p>
      </div>
      %include('static/footer.html')
    </div>
  </body>
</html>
