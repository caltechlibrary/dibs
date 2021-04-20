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

    <div class="row bg-light" style="margin: auto 0px">
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
   var myUV;

   window.addEventListener('uvLoaded', function (e) {
     myUV = createUV('#uv', {
       iiifResourceUri: '{{base_url}}/manifests/{{barcode}}',
       configUri: '{{base_url}}/static/uv-config.json'
     }, new UV.URLDataProvider());

     myUV.on("created", function(obj) {
       console.log('parsed metadata', myUV.extension.helper.manifest.getMetadata());
       console.log('raw jsonld', myUV.extension.helper.manifest.__jsonld);
     });

     // Calculate the delay to exiration (in msec) and force a reload then.
     var now = new Date().getTime();
     var end = new Date("{{js_end_time}}").getTime();
     var timeout = (end - now) + 1000;
     setTimeout(() => { window.location.reload(); }, timeout);

   }, false);

   window.onpageshow = function (event) {
     // If this page was loaded from cache, force a reload.
     if (event.persisted) {
       window.location.reload();
     }
   };
  </script>

  <script src="{{base_url}}/viewer/uv/uv.js"></script>

</body>
</html>
