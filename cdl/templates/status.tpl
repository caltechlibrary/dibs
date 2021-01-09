<!DOCTYPE html>
<html lang="en">

  <head>
    <title>List of items currently loaned out in the Caltech Digital Loan system</title>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link href="https://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">

    </script>

  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto" style="width: 400px; text-align: center">List of current loans</h2>
      <div class="d-grid gap-3">

        <div class="mb-3">
          <table class="table">
            <thead class="thead-light">
              <tr>
                <th scope="col">Barcode</th>
                <th scope="col">Title</th>
                <th scope="col">Patron</th>
                <th scope="col">Started</th>
                <th scope="col">End time</th>
              </tr>
            </thead>
            <tbody>
            %for loan in loans:
              <tr scope="row">
                <td>{{loan.item.barcode}}</td>
                <td><a target="_blank" rel="noopener noreferrer" href="https://caltech.tind.io/admin2/bibcirculation/get_item_details?ln=en&recid={{loan.item.tind_id}}">{{loan.item.title}}</a></td>
                <td>{{loan.patron}}</td>
                <td>{{loan.started.strftime("%Y-%m-%d %H:%M")}}</td>
                <td>{{loan.endtime.strftime("%Y-%m-%d %H:%M")}}</td>
              </tr>
            %end
            </tbody>
          </table>

          <div class="py-4">
            <div class="btn-toolbar mx-auto" style="width: 150px;">
              <button class="btn btn-primary mx-2" style="width: 150px"
                      onclick="window.location='/list';return false;"><span style="font-size: 20px; vertical-align: center">&larr;</span> Back to list</button></a>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </body>

</html>
