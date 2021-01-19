<!DOCTYPE html>
<html lang="en">
  <meta http-equiv="Pragma" content="no-cache">
  <head>
    <title>Description page for {{item.title}}</title>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script>
     // Reload the page if the user got here by clicking the back button.
     // Solution from https://stackoverflow.com/a/43043658/743730
     window.addEventListener( "pageshow", function ( event ) {
       var historyTraversal =
         event.persisted || (typeof window.performance != "undefined" && 
                             window.performance.navigation.type === 2);
       if (historyTraversal) {
         window.location.reload();
       }
     });

     // Implement simple AJAX data posting for the loan button and redirect
     // the browser to the location received as the response.
     $(function() {
       $('#btnLoan').click(function() {
         $.ajax({
           url: '/loan',
           data: $('form').serialize(),
           type: 'POST',
           success: function(response) {
             console.log(response);
             location.href = response;
           },
           error: function(error) {
             console.log(error);
           }
         });
       });
     });
    </script>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <style type="text/css">
      #btnLoan:disabled {
        cursor: not-allowed;
      }
      p .shown-if-not-available {
        font-weight: bold;
      }
    </style>

  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto my-2 w-100 text-center">
        {{item.title}}
      </h2>
      <h3 class="mx-auto w-100 text-center">
        <em>Author: {{item.author}}</em>
      </h3>
      <hr>

      <div class="py-4">
        <p class="mx-auto text-center" style="width: 400px">
          This title is currently <span class="shown-if-not-available">not</span>
          available for digital loan.
        </p>

        <form class="form-loan">
          <input type="hidden" name="inputBarcode" value="{{item.barcode}}"/>
          <div class="btn-toolbar mx-auto" style="width: 150px;">
            <button class="btn mx-auto" id="btnLoan" type="button">
              <span class="shown-if-available">Get loan</span>
              <span class="shown-if-not-available">Not available</span>
            </button>
          </div>
        </form>

        <p class="mx-auto text-center py-3" style="width: 400px">
          Loan duration: {{item.duration}} hours
        </p>
      </div>

      <script>
       // Toggle the visibility of the loan button depending on availability.
       // This needs to be done after the loan button is defined above,
       // which is why the code is down here.
       if ("{{available}}" != "True") {
         $('#btnLoan').prop('disabled', true);
         $('#btnLoan').addClass('btn-secondary');
         $(".shown-if-available").css("display", "none");
         $(".shown-if-not-available").css("display", "inline");
       } else {
         $('#btnLoan').prop('disabled', false);
         $('#btnLoan').addClass('btn-primary');
         $(".shown-if-available").css("display", "inline");
         $(".shown-if-not-available").css("display", "none");
       }
      </script>

  </body>
</html>
