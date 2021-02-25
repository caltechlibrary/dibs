<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Pragma" content="no-cache">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    %include('common/standard-inclusions.tpl')
    <link href="{{base_url}}/viewer/uv/uv.css" rel="stylesheet" type="text/css">

    <script src="{{base_url}}/viewer/uv/lib/offline.js"></script>
    <script src="{{base_url}}/viewer/uv/helpers.js"></script>

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
        <div class="float-left my-1"><p>Loan expires at {{endtime}}.</p></div>
      </div>
      <div class="col-6">
        <button type="button" class="btn btn-danger float-right my-1"
                onclick="if ( confirm('This will end your loan immediately. '
                                    + 'You will need to wait {{reloan_wait_time}} '
                                    + 'before being able to borrow this item again.'
                                    )) { window.location = '{{base_url}}/return/{{barcode}}';}
                                        else { return false; }">
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
       configUri: '{{base_url}}/viewer/uv-config.json'
     }, new UV.URLDataProvider());

     myUV.on("created", function(obj) {
       console.log('parsed metadata', myUV.extension.helper.manifest.getMetadata());
       console.log('raw jsonld', myUV.extension.helper.manifest.__jsonld);
     });
   }, false);

   window.onpageshow = function (event) {
     if (event.persisted) {
       window.location.reload();
     }
   };
  </script>

  <script src="uv/uv.js"></script>

</body>
</html>
