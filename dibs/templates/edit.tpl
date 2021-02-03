<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('static/banner.html')
  <head>
    %include('static/standard-inclusions.html')
    <title>Add or edit a Caltech DIBS entry</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{base_url}}/static/dibs.css">
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('static/navbar.html')

        <div class="w-75 text-center mx-auto">
          <form action="{{base_url}}/update/{{action}}" method="POST">

          <div class="w-75 text-center mx-auto">
            <form action="/update/{{action}}" method="POST">

              <label for="barcode" class="sr-only">Barcode</label>
              <input name="barcode" type="number" class="form-control"
                     placeholder="Barcode"
                     %if item:
                     value="{{item.barcode}}"
                     %end
                     required autofocus>

              <label for="numCopies" class="sr-only">Copies</label>
              <input name="num_copies" type="number" class="form-control"
                     placeholder="Number of copies to be made available for simultaneous loans"
                     step="any" min="1"
                     %if item:
                     value="{{item.num_copies}}"
                     %end
                     required>

              <label for="duration" class="sr-only">Loan duration (in hours)</label>
              <input name="duration" type="number" class="form-control"
                     placeholder="Maximum duration of a loan (in hours)"
                     step="any" min="1" oninput="check_nonzero(this)"
                     %if item:
                     value="{{item.duration}}"
                     %end
                     required>
              
              <div class="py-4">
                <div class="btn-toolbar mx-auto" style="width: 240px;">
                  <input class="btn btn-secondary mx-2" style="width: 100px"
                         name="cancel" value="Cancel" type="submit" formnovalidate/>
                  <input id="btnAdd" class="btn btn-primary mx-2" style="width: 100px"
                         name="add"
                         %if item:
                         value="Save"
                         %else:
                         value="Add"
                         %end
                         type="submit"/>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      %include('static/footer.html')
    </div>
  </body>
</html>
