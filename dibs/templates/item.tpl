<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    %include('common/standard-inclusions.tpl')

    <title>Description page for {{item.title}}</title>

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

    <style type="text/css">
      #btnLoan:disabled {
        cursor: not-allowed;
      }
    </style>

  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container">

        <table class="table table-borderless mt-4">
          <tbody>
            <tr>
              <td width="200px" style="border-top: none">
                %if item.thumbnail != '':
                <img class="img-thumbnail" src="{{item.thumbnail}}" style="width: 180px">
                %else:
                <img class="img-thumbnail" src="{{base_url}}/static/missing-thumbnail.svg" style="width: 180px">
                %end
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
            <form action="{{base_url}}/loan" method="POST"
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
         var refresher,
             btnLoan = document.getElementById('btnLoan'),
             when = document.getElementById('when');
             
         // Toggle the visibility of the loan button depending on availability.
         // This needs to be done after the loan button is defined above,
         // which is why the code is down here.
         if ("{{available}}" == "True") {
//FIXME: Replace with document.querySelector() or getElementByID(), removeAttribute()
// to removed the disabled state and use setAttribute() to set the value. Add classes
// with  classList.add() and classList.remove()
            btnLoan.removeAttribute('disabled'); 
            btnLoan.setAttribute('value', 'Get loan');
            btnLoan.classList.add('btn-primary', 'show-if-available');
            btnLoan.classList.remove('btn-secondary', 'shown-if-not-available');
            
/*            
           $('#btnLoan').prop('disabled', false);
           $('#btnLoan').prop('value', 'Get loan');
           $('#btnLoan').addClass('btn-primary');
           $(".shown-if-available").css("display", "inline");
           $(".shown-if-not-available").css("display", "none");
*/
         } else {
            btnLoan.setAttribute('disabled', true);
            btnLoan.setAttribute('value', 'Not available');
            btnLoan.classList.remove('btn-primary', 'shown-if-available');
            btnLoan.classList.add('btn-secondary', 'shown-if-not-available');
/*
           $('#btnLoan').prop('disabled', true);
           $('#btnLoan').prop('value', 'Not available');
           $('#btnLoan').addClass('btn-secondary');
           $(".shown-if-available").css("display", "none");
           $(".shown-if-not-available").css("display", "inline");
*/           
         }

//FIXME: This should be done in the CSS file as a class, we add/remove classes to cause this to happen
         if ("{{endtime}}" == "None") {
             when.setAttribute('style', 'display:none');
/*
           $('#when').css("display", "none");
*/
         } else {
             when.removeAttribute('style');
         }

         // Refresh the page automatically, so that if the user has it open
         // and someone else takes out a loan, the user has a better chance of
         // finding out as soon as possible.  This is not as good as using a
         // framework like React, but it's simpler.  This approach doesn't
         // flash the page like a meta refresh tag does.

//FIXME: We don't need the wrapping ready because we're not relying on anything outside of vanilla JS
/*
         $(document).ready(function(e) {
             refresher = setInterval('update_content();', 10000);
         })
*/

        //FIXME: We should have an end point for the item's status. We can fetch this status
        // might and use that to update the page without causing the page to reload.

        httpGet = function (url, contentType, callbackFn) {
            let self = this,
            xhr = new XMLHttpRequest(),
            page_url = new URL(window.location.href);
            xhr.onreadystatechange = function () {
                // process response
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status == 200) {
                        let data = xhr.responseText;
                        if (contentType === "application/json" && data !== "") {
                            data = JSON.parse(xhr.responseText);
                        }
                        callbackFn(data, "");
                    } else {
                        callbackFn("", xhr.status);
                    }
                }
            };

            /* we always want JSON data */
            xhr.open('GET', url, true);
            if (contentType !== "" ) {
                xhr.setRequestHeader('Content-Type', contentType);
            }
            xhr.send();
         };

         function update_content() {
//FIXME: Replace with XHR request per MDN JavaScript examples
            httpGet('{{base_url}}/item-status/{{item.barcode}}', 'text/plain',
                function(data, err) {
                    window.clearInterval(refresher);
                    if (! err) {
                        //FIXME: document write was depreciated in 2016.
                        // We want to use the handle to the specific
                        // elements we want to update and update the page in place.
                        console.log("DEBUG update page here...");
                        console.log(data);
                    } else {
                    	console.log("ERROR: " + err);
                    }
                });
            
/*
           $.ajax({
             type: "GET",
             url: "{{base_url}}/item/{{item.barcode}}",
             cache: false,
           })
            .done(function(page_html) {
              window.clearInterval(refresher);
              var newDoc = document.open("text/html");
              newDoc.write(page_html);
              newDoc.close();
            });
*/
         }
         refresher = setInterval(update_content, 10000);

        </script>
      </div>

      %include('common/footer.html')
    </div>
  </body>
</html>
