<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    %include('common/standard-inclusions.tpl')

    <title>Description page for {{item.title}}</title>

    <script>
     % setdefault('data', {})
     % setdefault('explanation', '')
     % setdefault('when_available', '')

     // Reload the page if the user got here by clicking the back button.
     // Solution from https://stackoverflow.com/a/43043658/743730
     window.addEventListener("pageshow", function (event) {
         var historyTraversal = event.persisted ||
                                (typeof window.performance != "undefined" && 
                                 window.performance.navigation.type === 2);
         if (historyTraversal) {
             console.info("Back button history traversal -- reloading page");
             window.location.reload(true);
         } else {
             var perfEntries = performance.getEntriesByType("navigation");
             if (Array.isArray(perfEntries) && typeof(perfEntries[0]) !== "undefined"
                 && perfEntries[0].type === "back_forward") {
                 console.log("Back button navigation -- reloading page");
                 window.location.reload(true);
             }
         }
     });
    </script>
  </head>
  
  <body onunload="">
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container">
        <table class="table table-borderless mt-4">
          <tbody>
            <tr>
              <td width="200px" style="border-top: none">
                %if item.thumbnail != '':
                <img class="img-thumbnail" src="{{item.thumbnail}}">
                %else:
                <img class="img-thumbnail" src="{{base_url}}/static/missing-thumbnail.svg">
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
                    %if item.edition != '':
                    <tr>
                      <th>Edition</th>
                      <td>{{item.edition}}</td>
                    </tr>
                    %end
                    <tr><td></td><td></td></tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>

        <div>
          <p class="mx-auto text-center w-75">
            This item is <span id="not-available">{{'' if available else 'not'}}</span>
            currently available to you for a digital loan.
            <span id="explanation">{{explanation}}</span>
            <span id="when">This item is scheduled to become available again
              no later than {{when_available}}.</span>
          </p>

          <div class="col-md-3 mx-auto text-center">
            <form action="{{base_url}}/loan" method="POST"
                  onSubmit="return confirm('This will start your {{item.duration}} '
                                           + 'hour loan period immediately. Proceed?'
                                           + '\n\nReminder: closing the viewer window '
                                           + 'will not end the loan  – please use the '
                                           + 'End Loan Now button when you are ready. '
                                           + 'You may also open the viewer in other '
                                           + 'devices during the loan period.');">
              <input type="hidden" name="barcode" value="{{item.barcode}}"/>
              <input id="loan-button" class="btn btn-block mx-auto"
                     style="width: 120px" type="submit"
                     value="{{'Get Loan' if available else 'Not Available'}}" {{'' if available else 'disabled'}} />
            </form>
          </div>

          <p class="mx-auto text-center w-50 pt-3">
            Loan duration: {{item.duration}} hours
          </p>
          <p id="refresh-tip" class="mx-auto text-center w-50 text-info">
            This page will refresh automatically.
          </p>
        </div>
        <script>
/* NOTE: these JavaScript functions are inlined to allow for template
rendered start conditions and to limit calls to server */
(function (document, window) {
    const max_poll_count = 360, /* max number to times to poll /item-status */
          wait_period = 10000;  /* wait period between polling /item-status */

    /* Get handles to the elements we need to change on pages */
    let loanButton = document.getElementById('loan-button'),
        notAvailableElement = document.getElementById('not-available'),
        explanationElement = document.getElementById('explanation'),
        refreshTip = document.getElementById('refresh-tip'),
        whenElement = document.getElementById('when');
     
    // Toggle the visibility of the loan button, expire times and explanation
    // depending on availability.
    function set_book_status(available, explanation, when_available) {
        if (available == true) {
            console.info("Book {{item.barcode}} is available");
            loanButton.removeAttribute('disabled');
            loanButton.setAttribute('value', 'Get loan');
            loanButton.classList.add('btn-primary');
            loanButton.classList.remove('btn-secondary');
            notAvailableElement.innerHTML = '';
            explanationElement.innerHTML = '';
            whenElement.innerHTML = '';
        } else {
            console.info("Book {{item.barcode}} is NOT available");
            loanButton.setAttribute('disabled', true);
            loanButton.setAttribute('value', 'Not available');
            loanButton.classList.remove('btn-primary');
            loanButton.classList.add('btn-secondary');
            notAvailableElement.innerHTML = 'not';
            if (typeof explanation !== "undefined" && explanation !== null
                && explanation !== "" && explanation != "None") {
              explanationElement.innerHTML = explanation;
            } else {
              console.warn('explanation is undefined');
              explanationElement.innerHTML = "";
            }
            if (typeof when_available !== "undefined" && when_available !== null
                && when_available !== "" && when_available != "None") {
              console.info("when_available = ", when_available);
              whenElement.innerHTML = 
                'This item will become available again by <nobr>'
                + when_available + '</nobr>.';
            } else {
              console.warn('when_available is undefined');
              whenElement.innerHTML = '';
            }
        }
    }
    
    if ("{{available}}" == "True") {
        set_book_status(true, '', '');
    } else {
        set_book_status(false, '{{explanation}}', '{{when_available}}');
    }

    /* This is a simple http GET function. It is based on examples
    at MDN Developer site and the satirical Vanilla JS framework site */
    httpGet = function (url, contentType, callbackFn) {
        let self = this,
        xhr = new XMLHttpRequest(),
        page_url = new URL(window.location.href);
        xhr.onreadystatechange = function () {
            /* process response */
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status == 200) {
                    let data = xhr.responseText;
                    if (contentType === "application/json" && data !== "") {
                      data = JSON.parse(xhr.responseText);
                    }
                    callbackFn(data, "");
                } else {
                    console.warn('xhr status = ', xhr.status)
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
                console.warn("Reached max poll count");
                refreshTip.innerHTML = 'Auto-refresh paused. Reload this browser window to see updates.';
                refreshTip.classList.add('text-danger');
                window.clearInterval(refresher);
            } else {
                poll_count++;
            }
            if (! err) {
                /*FIXME: document write was depreciated in 2016.
                 We want to use the handle to the specific
                 elements we want to update and update the page in place.
                */
                console.info("Updating status: data = ", data);
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
