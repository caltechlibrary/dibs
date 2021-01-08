<!DOCTYPE html>
<html lang="en">

  <head>
    <title>Add an item to the Caltech Digital Loan system</title>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link href="https://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>

    <script>
     $(function() {
       $('#btnAdd').click(function() {
         $.ajax({
           url: '/add',
           data: $('form').serialize(),
           type: 'POST',
           success: function(response) {
             console.log(response);
             location.href = "/list";
           },
           error: function(error) {
             console.log(error);
           }
         });
       });
     });
    </script>

  </head>

  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto" style="width: 400px; text-align: center">Add a new item</h2>
      <div class="d-grid">

        <div class="jumbotron">
          <form class="form-add">
            <label for="inputBarcode" class="sr-only">Barcode</label>
            <input type="barcode" name="inputBarcode" id="inputBarcode" class="form-control" placeholder="Barcode" required autofocus>
            <label for="inputTitle" class="sr-only">Title</label>
            <input type="title" name="inputTitle" id="inputTitle" class="form-control" placeholder="Title" required>
            <label for="inputAuthor" class="sr-only">Author</label>
            <input type="author" name="inputAuthor" id="inputAuthor" class="form-control" placeholder="Author" required>
            <label for="inputTindId" class="sr-only">TindId</label>
            <input type="tindId" name="inputTindId" id="inputTindId" class="form-control" placeholder="TIND Id" required>
            <label for="inputCopies" class="sr-only">Copies</label>
            <input type="copies" name="inputCopies" id="inputCopies" class="form-control" placeholder="# copies to be made available" required>
            
            <div class="py-4">
              <div class="btn-toolbar mx-auto" style="width: 240px;">
                <button class="btn btn-default mx-2" style="width: 100px" type="reset"
                        onclick="window.location='/list';return false;">Cancel</button></a>
                <button class="btn btn-primary mx-2" style="width: 100px"
                        id="btnAdd" type="button">Add</button>
              </div>
            </div>
          </form>
        </div>


      </div>
    </div>
  </body>

</html>
