<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    %include('common/standard-inclusions.tpl')
    <link href="{{base_url}}/viewer/uv/uv.css" rel="stylesheet" type="text/css">

    <script src="{{base_url}}/viewer/uv/lib/offline.js"></script>
    <script src="{{base_url}}/viewer/uv/helpers.js"></script>
    <script>
     function maybeEndLoan() {
       if (confirm('This will end your loan immediately. You will need to wait '
                 + '{{wait_time}} before borrowing this item again.')) {

         var form = document.createElement('form');
         form.setAttribute('id', 'returnButton');
         form.setAttribute('method', 'post');
         form.setAttribute('action', '{{base_url}}/return/{{barcode}}');
         form.style.display = 'hidden';
         document.body.appendChild(form)

         var input = document.createElement('input');
         input.setAttribute('type', 'hidden');
         input.setAttribute('name', 'barcode');
         input.setAttribute('value', '{{barcode}}');
         document.getElementById('returnButton').appendChild(input);

         log('user ended loan explicitly');
         form.submit();
       } else {
         return false;
       }
     }
    </script>

    <style>
     html, body { height: 97% }
     #uv {
       min-width: 600px;
       min-height: 600px;
     }
    </style>

    <title>Caltech DIBS</title>
</head>
<body>
    
  <div class="container-fluid h-100 w-100 text-center">
    <p id="no-javascript" class="alert alert-danger mx-auto text-center w-75 mt-4">
      Note: JavaScript is disabled in your browser.
      This site cannot function properly without JavaScript.
      Please enable JavaScript and reload this page.
    </p>
    <p id="no-cookies" class="d-none alert alert-danger mx-auto text-center w-75 mt-4">
      Note: web cookies are blocked by your browser.
      The document viewer cannot function properly without cookies.
      Please allow cookies from this site in your browser, and reload this page.
    </p>
    <div id="loan-info" class="d-none row bg-light" style="margin: auto 0px">
      <div class="col-6">
        <div class="float-left my-1"><p>Loan expires at {{end_time}}.</p></div>
      </div>
      <div class="col-6">
        <button type="button" class="btn btn-danger float-right my-1"
                onclick="maybeEndLoan();">
          End loan now</button>
      </div>
    </div>

    <div class="row h-100">
      <div id="uv" class="col-12 mb-2"></div>
    </div>

  </div>

  <script>
   let noJSElement      = document.getElementById('no-javascript'),
       noCookiesElement = document.getElementById('no-cookies'),
       loanInfoElement  = document.getElementById('loan-info');

   var myUV;

   window.addEventListener('uvLoaded', function (e) {
     log('uvLoaded listener called');

     myUV = createUV('#uv', {
       iiifResourceUri: '{{base_url}}/manifests/{{barcode}}',
       configUri: '{{base_url}}/static/uv-config.json'
     }, new UV.URLDataProvider());

     myUV.on("created", function(obj) {
       log('parsed metadata', myUV.extension.helper.manifest.getMetadata());
     });

     // Calculate the delay to exiration (in msec) and force a reload then.
     var now = new Date().getTime();
     var end = new Date("{{js_end_time}}").getTime();
     var timeout = (end - now) + 1000;
     setTimeout(() => { window.location.reload(); }, timeout);
   }, false);

   window.onpageshow = function (event) {
     // If we can run this, we have JS, so turn off the warning.
     noJSElement.classList.add('d-none');
     // If cookies are not enabled, leave the cookies message & quit.
     if (navigator.cookieEnabled == 0) {
       noCookiesElement.classList.remove('d-none');
       loanInfoElement.classList.add('d-none');
       log('cookies are blocked by the browser -- stopping');
       return;
     } else {
       noCookiesElement.classList.add('d-none');
       loanInfoElement.classList.remove('d-none');
     };

     // If this page was loaded from cache, force a reload.
     if (event.persisted) {
       log('forcing page reload');
       window.location.reload();
     };
   };
  </script>

  <script src="{{base_url}}/viewer/uv/uv.js"></script>

</body>
</html>

<!--
Local Variables:
js-indent-level: 2
End:
-->
