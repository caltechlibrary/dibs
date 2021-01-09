<!DOCTYPE html>
<html lang="en">

  <head>
    <title>List of items currently available in the Caltech Digital Loan system</title>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link href="https://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">

    </script>

  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto" style="width: 400px; text-align: center">List of available items</h2>
      <div class="d-grid gap-3">

        <div class="mb-3">
          <table class="table">
            <thead class="thead-light">
              <tr>
                <th scope="col">Barcode</th>
                <th scope="col">Title</th>
                <th scope="col">Author</th>
                <th scope="col" align="center">TIND</th>
                <th scope="col" align="center">Loan copies</th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
            %for item in items:
              <tr scope="row">
                <td>{{item.barcode}}</td>
                <td><a href="">{{item.title}}</a></td>
                <td>{{item.author}}</td>
                <td><a target="_blank" rel="noopener noreferrer" href="https://caltech.tind.io/admin2/bibcirculation/get_item_details?ln=en&recid={{item.tind_id}}">{{item.tind_id}}</a></td>
                <td align="center">{{item.num_copies}}</td>
                <td><a href="" class="btn btn-secondary btn-sm">Share link</a></td>
                <form action="/remove" method="POST"
                      onSubmit="return confirm('Remove {{item.barcode}} (&#8220;{{item.title}}&#8221; by {{item.author}})? This will not delete the files from storage, but will remove the entry from the loan database.');">
                  <input type="hidden" name="barcode" value="{{item.barcode}}">
                  <td><input type="submit" name="Remove" value="Remove" class="btn btn-danger btn-sm"/></td>
                </form>
              </tr>
            %end
            </tbody>
          </table>
        </div>

        <div class="py-3 mx-auto" style="width: 150px">
          <a href="/add" class="btn btn-primary m-0">Add new item</a>
        </div>
      </div>
    </div>
  </body>

</html>
