<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('static/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">

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
    </script>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <style type="text/css">
      #btnLoan:disabled {
        cursor: not-allowed;
      }
    </style>

  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      <div class="container">

        <table class="table table-borderless pt-3">
          <tbody>
            <tr>
              <td width="200px" style="border-top: none">
                <img class="img-thumbnail" src="{{item.thumbnail}}" style="width: 180px">
              </td>
              <td style="border-top: none">
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <th width="120em">Title</th>
                      <td>
                        <strong>
                          %if item.tind_id != '':
                          <a target="_blank"
                             href="https://caltech.tind.io/record/{{item.tind_id}}">{{item.title}}</a>
                          %else:
                          {{item.title}}
                          %end
                        </strong>
                      </td>
                    </tr>
                    <tr>
                      <th>Author(s)</th>
                      <td>{{item.author}}</td>
                    </tr>
                    <tr>
                      <th>Year</th>
                      <td>{{item.year}}</td>
                    </tr>
                    <tr>
                      <th>Edition</th>
                      %if item.edition != '':
                      <td>{{item.edition}}</td>
                      %else:
                      <i>Unknown</i>
                      %end
                    </tr>
                    <tr><td></td><td></td></tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>

        <div>
          <p class="mx-auto text-center" style="width: 500px">
            This item is <span class="shown-if-not-available">not</span> currently
            available to you for a digital loan.
            <span class="shown-if-not-available">{{explanation}}</span>
            <span id="when" class="shown-if-not-available">This item will become
              available again at
              {{endtime.strftime("%I:%M %p on %Y-%m-%d") if endtime else 'unknown'}}.</span>
          </p>

          <div class="col-md-3 mx-auto text-center">
            <form action="/loan" method="POST"
                  onSubmit="return confirm('This will start your {{item.duration}} hour loan period immediately. Proceed?');">
              <input type="hidden" name="barcode" value="{{item.barcode}}"/>
              <input id="btnLoan" class="btn btn-block mx-auto" style="width: 120px" type="submit"/>
            </form>
          </div>

          <p class="mx-auto text-center w-50 py-3">
            Loan duration: {{item.duration}} hours
          </p>
        </div>
        <script>
         // Toggle the visibility of the loan button depending on availability.
         // This needs to be done after the loan button is defined above,
         // which is why the code is down here.
         if ("{{available}}" == "True") {
           $('#btnLoan').prop('disabled', false);
           $('#btnLoan').prop('value', 'Get loan');
           $('#btnLoan').addClass('btn-primary');
           $(".shown-if-available").css("display", "inline");
           $(".shown-if-not-available").css("display", "none");
         } else {
           $('#btnLoan').prop('disabled', true);
           $('#btnLoan').prop('value', 'Not available');
           $('#btnLoan').addClass('btn-secondary');
           $(".shown-if-available").css("display", "none");
           $(".shown-if-not-available").css("display", "inline");
         }

         if ("{{endtime}}" == "None") {
           $('#when').css("display", "none");
         }

         // Refresh the page automatically, so that if the user has it open
         // and someone else takes out a loan, the user has a better chance of
         // finding out as soon as possible.  This is not as good as using a
         // framework like React, but it's simpler.  This approach doesn't
         // flash the page like a meta refresh tag does.

         var refresher;
         $(document).ready(function(e) {
           refresher = setInterval("update_content();", 10000);
         })

         function update_content() {
           $.ajax({
             type: "GET",
             url: "/item/{{item.barcode}}",
             cache: false,
           })
            .done(function(page_html) {
              window.clearInterval(refresher);
              var newDoc = document.open("text/html");
              newDoc.write(page_html);
              newDoc.close();
            });   
         }
         
        </script>
      </div>
      %include('static/footer.html')
    </div>
  </body>
</html>
