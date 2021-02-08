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
            This item is <span id="not-available">{{'' if available else 'not'}}</span> currently
            available to you for a digital loan.
            <span id="explanation">{{explanation}}</span></div>
            <span id="when">This item will become
              available again at
              {{endtime.strftime("%I:%M %p on %Y-%m-%d") if endtime else 'unknown'}}.</span>
          </p>

          <div class="col-md-3 mx-auto text-center">
            <form action="{{base_url}}/loan" method="POST"
                  onSubmit="return confirm('This will start your {{item.duration}} hour loan period immediately. Proceed?');">
              <input type="hidden" name="barcode" value="{{item.barcode}}"/>
              <input id="loan-button" class="btn btn-block mx-auto" style="width: 120px" type="submit" value="{{'Get Loan' if available else 'Not Available'}}" {{'' if available else 'disabled'}} />
            </form>
          </div>

          <p class="mx-auto text-center w-50 py-3">
            Loan duration: {{item.duration}} hours
          </p>
        </div>
        <script>
/* NOTE: these JavaScript functions are inlined to allow for template
rendered start conditions and to limit calls to server */
(function (document, window) {
	const max_poll_count = 10, /* maximum number to times to poll /item-status */
		  wait_period = 10000; /* wait period between polling /item-status */

    /* Get handles to the elements we need to change on pages */
	let loanButton = document.getElementById('loan-button'),
	    notAvailableElement = document.getElementById('not-available'),
		explanationElemement = document.getElementById('explanation'),
		whenElemement = document.getElementById('when');
     
	// Toggle the visibility of the loan button, expire times and explanation
	// depending on availability.
	function set_book_status(available, explanation, endtime) {
		if (available == true) {
			console.log("DEBUG book is available");
			loanButton.removeAttribute('disabled');
			loanButton.setAttribute('value', 'Get loan');
			loanButton.classList.add('btn-primary');
			loanButton.classList.remove('btn-secondary');
			notAvailableElement.innerHTML = '';
			explanationElemement.innerHTML = '';
			whenElemement.innerHTML = '';
		} else {
			console.log("DEBUG book is NOT available");
			loanButton.setAttribute('disabled', true);
			loanButton.setAttribute('value', 'Not available');
			loanButton.classList.remove('btn-primary');
			loanButton.classList.add('btn-secondary');
			notAvailableElement.innerHTML = 'not';
			explanationElemement.innerHTML = explanation;
			whenElement.innerHTML = endtime;
		}
	}
	
	if ("{{available}}" == "True") {
		set_book_status(true, '', '');
	} else {
		set_status(false, '{{explanation}}', '{{endtime.strftime("%I:%M %p on %Y-%m-%d") if endtime else "unknown"}}');
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
	httpGet('{{base_url}}/item-status/{{item.barcode}}', 'text/plain',
		function(data, err) {
			if (poll_count > 12) {
		    	window.clearInterval(refresher);
		    } else {
		    	poll_count++;
		    }
		    if (! err) {
		        /*FIXME: document write was depreciated in 2016.
		         We want to use the handle to the specific
		         elements we want to update and update the page in place.
		        */
		        console.log("DEBUG update page here...");
		        console.log(data);
		    } else {
		    	console.log("ERROR: " + err);
		    }
		});
	}, wait_period);

}(document, window));
        </script>
      </div>

      %include('common/footer.html')
    </div>
  </body>
</html>
