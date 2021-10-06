<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"/>
    <meta http-equiv="Pragma" content="no-cache"/>
    <meta http-equiv="Expires" content="0"/>
    %include('common/standard-inclusions.tpl')

    <title>Description page for {{item.title}}</title>

    <script>
     // Reload the page if the user got here by clicking the back button.
     // Adapted from answers to https://stackoverflow.com/q/43043113/743730
     window.addEventListener("pageshow", function (event) {
       var historyTraversal = event.persisted ||
                              (typeof window.performance != "undefined" && 
                               window.performance.navigation.type === 2);
       if (historyTraversal) {
         log("Back button history traversal -- reloading page");
         window.location.reload(true);
       } else {
         var perfEntries = performance.getEntriesByType("navigation");
         if (Array.isArray(perfEntries) && typeof(perfEntries[0]) !== "undefined"
             && perfEntries[0].type === "back_forward") {
           log("Back button navigation -- reloading page");
           window.location.reload(true);
         }
       }
     });
    </script>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')
      %from os import stat
      %from os.path import join, exists

      <div class="container main-container">
        <div class="row pt-3 mx-auto item-info-row">

          <div class="col-sm-9 col-xs-12 item-info my-auto">
            <table class="item-info-table table table-sm">
              <tbody>
                <tr>
                  <th class="item-info-label">Title</th>
                  <td class="item-info-value">
                    <strong>
                      %if item.item_page != '':
                      <a target="_blank" href="{{item.item_page}}">{{item.title}}</a>
                      %else:
                      {{item.title}}
                      %end
                    </strong>
                  </td>
                </tr>

                <tr>
                  <th>Author(s)</th>
                  <td class="item-info-value">
                    %author = item.author
                    {{author.split(',')[0] + ' et al.' if author.count(',') > 2 else author}}
                  </td>
                </tr>

                <tr>
                  <th>Year</th>
                  <td class="item-info-value">{{item.year}}</td>
                </tr>

                %if item.publisher != '':
                <tr
                  %if item.edition == '':
                  class="last"
                  %end
                  >
                  <th>Publisher</th>
                  <td class="item-info-value">{{item.publisher}}</td>
                </tr>
                %end

                %if item.edition != '':
                <tr class="last">
                  <th>Edition</th>
                  <td class="item-info-value">{{item.edition}}</td>
                </tr>
                %end
              </tbody>
            </table>
          </div>

          <div class="col-sm-2 col-xs-0 item-thumbnail">
            %thumbnail_file = join(thumbnails_dir, item.barcode + ".jpg")
            %if exists(thumbnail_file):
              %timestamp = stat(thumbnail_file).st_mtime
            <img class="thumbnail thumbnail-image img-responsive"
                 src="{{base_url}}/thumbnails/{{item.barcode}}.jpg?{{timestamp}}">
            %else:
            <img class="thumbnail img-responsive"
                 src="{{base_url}}/static/missing-thumbnail.svg">
            %end
          </div>

        </div>

        <div class="loan-info mt-5 pt-5">
          <p class="mx-auto text-center w-75 mt-2">
            <span id="available">This item is currently not available
              to you for a digital loan.</span>
            <span id="explanation"></span>
            <span id="when"></span>
          </p>

          <div class="col-md-3 mx-auto text-center">
            <form action="{{base_url}}/loan" method="POST"
                  onSubmit="return confirm('This will start your {{item.duration}} '
                                           + 'hour loan period immediately.'
                                           + '\n\nReminder: closing the viewer window '
                                           + 'will not end the loan  – please use the '
                                           + 'End Loan button when you are ready.'
                                           + '\n\nYou may open the viewer in other '
                                           + 'devices during the loan period.');">
              <input type="hidden" name="barcode" value="{{item.barcode}}"/>
              <input id="loan-button" class="d-none btn btn-block mx-auto mb-3"
                     type="submit" value="Not Available" disabled />
            </form>
          </div>

          <p id="no-javascript" class="delayed alert alert-danger mx-auto text-center w-75">
            Note: JavaScript is disabled in your browser.
            This site cannot function properly without JavaScript.
            Please enable JavaScript and reload this page.
          </p>
          <p id="no-cookies" class="d-none delayed alert alert-danger mx-auto text-center w-75">
            Note: web cookies are blocked by your browser.
            The document viewer cannot function properly without cookies.
            Please allow cookies from this site in your browser, and reload this page.
          </p>
          <p class="mx-auto text-center w-75">
            Loan duration: {{item.duration}} hours
          </p>
          <p id="refresh-tip" class="d-none mx-auto text-center w-75 text-info">
            This page will refresh automatically.
          </p>
        </div>

        <script>
         %setdefault('data', {})
         %setdefault('explanation', '')
         %setdefault('when_available', '')

         // NOTE: these JavaScript functions are inlined to allow for template
         // rendered start conditions and to limit calls to server.
         (function (document, window) {
           const max_poll_count = 360,    /* max # times to poll /item-status */
                 wait_period    = 10000;  /* wait bet. polls of /item-status */

           // Get handles to the elements we need to change on the page.
           let loanButton         = document.getElementById('loan-button'),
               availableElement   = document.getElementById('available'),
               explanationElement = document.getElementById('explanation'),
               whenElement        = document.getElementById('when'),
               refreshTip         = document.getElementById('refresh-tip'),
               noJSElement        = document.getElementById('no-javascript'),
               noCookiesElement   = document.getElementById('no-cookies');
           
           // Toggle the visibility of the loan button, expire times and
           // explanation depending on availability.
           function set_book_status(available, explanation, when_available) {
             noJSElement.classList.add('d-none');
             if (navigator.cookieEnabled == 0) {
               // Cookies not enabled. Leave the cookies message & quit.
               noCookiesElement.classList.remove('d-none');
               loanButton.classList.add('d-none');
               availableElement.innerHTML = 'This item is currently not available '
                                          + 'for a new digital loan.';
               log('Cookies are blocked by the browser -- stopping')
               return;
             } else {
               noCookiesElement.classList.add('d-none');
             };
             if (available == true) {
               log("Book {{item.barcode}} is available");
               loanButton.classList.remove('d-none');
               loanButton.removeAttribute('disabled');
               loanButton.setAttribute('value', 'Get loan');
               loanButton.classList.add('btn-primary');
               loanButton.classList.remove('btn-secondary');
               availableElement.innerHTML = 'This item is available '
                                          + 'for a digital loan.';
               explanationElement.innerHTML = '';
               whenElement.innerHTML = '';
             } else {
               log("Book {{item.barcode}} is NOT available");
               loanButton.classList.remove('d-none');
               loanButton.setAttribute('disabled', true);
               loanButton.setAttribute('value', 'Not available');
               loanButton.classList.remove('btn-primary');
               loanButton.classList.add('btn-secondary');
               availableElement.innerHTML = 'This item is currently not available '
                                          + 'for a new digital loan.';
               if (typeof explanation !== "undefined" && explanation !== null
                   && explanation !== "" && explanation != "None") {
                 explanationElement.innerHTML = explanation;
               } else {
                 log('explanation is undefined');
                 explanationElement.innerHTML = "";
               }
               if (typeof when_available !== "undefined" && when_available !== null
                   && when_available !== "" && when_available != "None") {
                 log("when_available = ", when_available);
                 whenElement.innerHTML =
                   'This item is scheduled to become available again '
                   + 'no later than <nobr>' + when_available + '</nobr>.';
               } else {
                 log('when_available is undefined');
                 whenElement.innerHTML = '';
               }
             }
           }
           
           if ("{{available}}" == "True") {
             set_book_status(true, '', '');
           } else {
             set_book_status(false, '{{explanation}}', '{{when_available}}');
           }

           /* NOTE: This is our refresher service (for book status updates). 
              The service is created with setIneterval and will run
              max_poll_count times at an interval set by wait_period.
            */
           let refresher,
               poll_count = 0;

           refresher = setInterval(function() {
             httpGet('{{base_url}}/item-status/{{item.barcode}}', 'application/json',
                     function(data, err) {
                       if (poll_count >= max_poll_count) {
                         log("Reached max poll count");
                         refreshTip.innerHTML = 'Auto-refresh paused. Reload this '
                                              + 'browser window to see updates.';
                         refreshTip.classList.add('text-danger');
                         window.clearInterval(refresher);
                       } else {
                         refreshTip.classList.remove('d-none');
                         refreshTip.classList.remove('text-danger');
                         poll_count++;
                       }
                       if (! err) {
                         /*FIXME: document write was depreciated in 2016.
                            We want to use the handle to the specific
                            elements we want to update and update the page in place.
                          */
                         log("Updating status: data = ", data);
		         set_book_status(data.available, data.explanation, data.when_available);
                       } else {
                         console.error("ERROR: " + err);
                       }
             });
           }, wait_period);
         }(document, window));

        </script>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>

<!--
Local Variables:
js-indent-level: 2
End:
-->
