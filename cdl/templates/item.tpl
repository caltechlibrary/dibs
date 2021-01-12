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
      #not-available {
        display: none;
        font-weight: bold;
      }
    </style>

  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto" style="width: 100%; text-align: center">
        {{item.title}}
      </h2>
      <h3 class="mx-auto" style="width: 400px; text-align: center">
        <em>by {{item.author}}</em>
      </h3>
      <hr>

      <div class="py-4">
        <p class="mx-auto" style="width: 400px; text-align: center">
          This title is currently <span id="not-available">not</span> available for digital loan.
        </p>
        <p class="mx-auto" style="width: 400px; text-align: center">
          Loan duration: {{item.duration}} hours
        </p>

        <form class="form-loan">
          <input type="hidden" name="inputBarcode" value="{{item.barcode}}"/>
          <div class="btn-toolbar mx-auto" style="width: 100px;">
            <button class="btn btn-primary mx-2" style="width: 100px"
                    id="btnLoan" type="button">
              Get loan
            </button>
          </div>
        </form>

      </div>

      <script>
       // Set the visibility of the loan button depending on availability.
       // This needs to be done after the loan button is defined above.
       const loanButton = document.getElementById('btnLoan');
       if ("{{available}}" != "True") {
         loanButton.disabled = "disabled";
         $("#not-available").css("display", "inline");
       }
      </script>

  </body>
</html>
