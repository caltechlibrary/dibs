<!DOCTYPE html>
<html lang="en">

  <head>
    <title>List of items currently available in the Caltech Digital Loan system</title>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link href="https://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">

  </head>
  
  <body>
    <div class="container-fluid">
  
      <h2>List of available items</h2>

        <table class="table">
          <thead class="thead-light">
            <tr>
              <th scope="col">Barcode</th>
              <th scope="col">Title</th>
              <th scope="col">TIND Record</th>
              <th scope="col">Num. copies</th>
            </tr>
          </thead>
          <tbody>
          %for item in items:
            <tr scope="row">
              <td>{{item.barcode}}</td>
              <td>{{item.title}}</td>
              <td>{{item.tind_id}}</td>
              <td>{{item.num_copies}}</td>
            </tr>
          %end
          </tbody>
        </table>

    </div>
  </body>

</html>
