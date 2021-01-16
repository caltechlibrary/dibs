<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link  href="/viewer/uv/uv.css" rel="stylesheet" type="text/css">
    <script src="/viewer/uv/lib/offline.js"></script>
    <script src="/viewer/uv/helpers.js"></script>
    <title>UV Hello World</title>
    <style>
     #uv {
       width: 800px;
       height: 600px;
     }
    </style>
</head>
<body>
    
    <div id="uv" class="uv"></div>

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
