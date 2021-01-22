<!DOCTYPE html>
<html lang="en">

  <head>
    <title>Add an item to Caltech DIBS</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto text-center w-100">Add a new item to DIBS</h2>
      <div class="d-grid">

        <div class="jumbotron">
          <form class="form-add" action="/add" method="POST">

            <label for="inputBarcode" class="sr-only">Barcode</label>
            <input type="barcode" name="inputBarcode" class="form-control"
                   placeholder="Barcode" required autofocus>

            <label for="inputTitle" class="sr-only">Title</label>
            <input type="title" name="inputTitle" class="form-control"
                   placeholder="Title" required>

            <label for="inputAuthor" class="sr-only">Author</label>
            <input type="author" name="inputAuthor" class="form-control"
                   placeholder="Author" required>

            <label for="inputTindId" class="sr-only">TindId</label>
            <input type="tindId" name="inputTindId" class="form-control"
                   placeholder="TIND Id">

            <label for="inputCopies" class="sr-only">Copies</label>
            <input type="copies" name="inputCopies" class="form-control"
                   placeholder="# copies to be made available" required>

            <label for="inputDuration" class="sr-only">Loan duration (in hours)</label>
            <input type="duration" name="inputDuration" class="form-control"
                   placeholder="hours per loan" required>
            
            <div class="py-4">
              <div class="btn-toolbar mx-auto" style="width: 240px;">
                <input class="btn btn-default mx-2" style="width: 100px"
                       type="reset" name="Cancel" value="Cancel"
                       onclick="window.location='/list';return false;"/>
                <input id="btnAdd" class="btn btn-primary mx-2" style="width: 100px"
                       value="Add" type="submit"/>
              </div>
            </div>
          </form>
        </div>


      </div>
    </div>
  </body>

</html>
