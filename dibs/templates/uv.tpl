<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    %include('common/standard-inclusions.tpl')
    <link href="{{base_url}}/static/dibs-uv.css" rel="stylesheet" type="text/css">

    <script type="text/javascript" src="{{base_url}}/viewer/lib/offline.js"></script>
    <script type="text/javascript" src="{{base_url}}/viewer/helpers.js"></script>

    <title>{{title}}</title>
</head>
<body>
    
  <div class="container-fluid h-100 w-100 text-center">
    <p id="no-javascript" class="delayed alert alert-danger mx-auto text-center w-75 mt-4">
      Note: JavaScript is disabled in your browser.
      This site cannot function properly without JavaScript.
      Please enable JavaScript and reload this page.
    </p>
    <p id="no-cookies" class="d-none delayed alert alert-danger mx-auto text-center w-75 mt-4">
      Note: web cookies are blocked by your browser.
      The document viewer cannot function properly without cookies.
      Please allow cookies from this site in your browser, and reload this page.
    </p>
    <div class="row h-100">
      <div id="uv"></div>
    </div>
  </div>

  <script type="text/javascript">
   let   noJSElement      = document.getElementById('no-javascript');
   let   noCookiesElement = document.getElementById('no-cookies');
   const wait_period      = 15000;  // wait bet. polls of /item-status
   let   poll_count       = 0;
   let   refresher;
   var   dibsUV;

   function loanCheck() {
     httpGet('{{base_url}}/item-status/{{barcode}}',
             'application/json',
             function(status, error) {
               if (error) {
                 console.error("ERROR: " + error);
                 return;
               };

               log('Loan status for {{barcode}} = ', status);
               if (! status.loaned_by_user) {
                 log('{{barcode}} is no longer available to this user');
                 window.location.reload();
               };
               poll_count++;
             });
   }

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

       log('User ended loan explicitly');
       form.submit();
     } else {
       return false;
     }
   }

   function expirationTimeInfo () {
     const infoElement = document.createElement('div');
     infoElement.setAttribute('id', 'expiration-info');
     const html = '<span class="expiration-info">Loan ends {{end_time}}</span>';
     infoElement.innerHTML = html;
     return infoElement;
   }

   function endLoanButton () {
     const buttonElement = document.createElement('div');
     buttonElement.setAttribute('id', 'end-loan-button');
     const html = '<button type="button" class="end-loan-button btn-danger"'
                + ' onclick="maybeEndLoan();">End loan</button>';
     buttonElement.innerHTML = html;
     return buttonElement;
   }

   // Hook ourselves into the UV viewer.
   window.addEventListener('uvLoaded', function (e) {
     log('uvLoaded listener called');

     urlDataProvider = new UV.URLDataProvider(true);
     var formattedLocales;
     var locales = urlDataProvider.get('locales', '');

     if (locales) {
       var names = locales.split(',');
       formattedLocales = [];
       for (var i in names) {
         var nameparts = String(names[i]).split(':');
         formattedLocales[i] = {name: nameparts[0], label: nameparts[1]};
       }
     } else {
       formattedLocales = [{ name: 'en-GB' }];
     }
     log('formattedLocales = ', formattedLocales);

     dibsUV = createUV('#uv', {
       root            : '.',
       iiifResourceUri : '{{base_url}}/manifests/{{barcode}}',
       configUri       : '{{base_url}}/static/uv-config.json',
       collectionIndex : Number(urlDataProvider.get('c', 0)),
       sequenceIndex   : Number(urlDataProvider.get('s', 0)),
       canvasIndex     : Number(urlDataProvider.get('cv', 0)),
       rangeId         : urlDataProvider.get('rid', 0),
       rotation        : Number(urlDataProvider.get('r', 0)),
       xywh            : urlDataProvider.get('xywh', ''),
       locales         : formattedLocales
     }, urlDataProvider);

     dibsUV.on("created", function(obj) {
       let uvOptions = document.getElementsByClassName('options');
       let uvTop = uvOptions[0];
       uvTop.insertBefore(expirationTimeInfo(), uvTop.firstChild);

       let rightOptions = document.getElementsByClassName('rightOptions');
       let rightDiv = rightOptions[0];
       rightDiv.insertBefore(endLoanButton(), rightDiv.firstChild);

       // Write some info useful when debugging.
       log('parsed metadata', dibsUV.extension.helper.manifest.getMetadata());
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
       log('Cookies are blocked by the browser -- stopping');
       return;
     } else {
       noCookiesElement.classList.add('d-none');
       log('Starting loan checker');
       refresher = setInterval(loanCheck, wait_period);
     };

     // If this page was loaded from cache, force a reload.
     if (event.persisted) {
       log('Forcing page reload');
       window.location.reload();
     };
   };
  </script>

  <script type="text/javascript" src="{{base_url}}/viewer/uv.js"></script>

</body>
</html>

<!--
Local Variables:
js-indent-level: 2
End:
-->
