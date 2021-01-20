<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link href="/viewer/uv/uv.css" rel="stylesheet" type="text/css">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet">
    <script src="/viewer/uv/lib/offline.js"></script>
    <script src="/viewer/uv/helpers.js"></script>
    <title>Caltech DIBS</title>
    <style>
     html, body { height: 97% }
     #uv {
       min-width: 600px;
       min-height: 600px;
     }
    </style>
</head>
<body>
    
  <div class="container-fluid h-100 w-100 text-center">

    <div class="row bg-light" style="margin: auto 0px">
      <div class="col-6">
        <div class="float-left my-1"><p>Loan expires at {{endtime.strftime("%I:%M %p %Z on %A, %B %d")}}.</p></div>
      </div>
      <div class="col-6">
        <button type="button" class="btn btn-danger float-right my-1"
                onclick="if(confirm('This will end your loan immediately. The loan policy is that you will have to wait one hour before making another loan.')){window.location='/return/{{barcode}}';}else{return false;}">
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
       iiifResourceUri: '/manifests/{{barcode}}',
       configUri: '/viewer/uv-config.json'
     }, new UV.URLDataProvider());

     myUV.on("created", function(obj) {
       console.log('parsed metadata', myUV.extension.helper.manifest.getMetadata());
       console.log('raw jsonld', myUV.extension.helper.manifest.__jsonld);
     });
   }, false);

  </script>
  <script src="uv/uv.js"></script>

</body>
</html>
