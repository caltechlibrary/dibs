<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Add or edit a Caltech DIBS entry</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{base_url}}/static/dibs.css">
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container text-center mx-auto mt-4">
        <form class="form-horizontal" action="{{base_url}}/update/{{action}}" method="POST">

          <label for="barcode" class="form-group control-label" style="display: block">
            <span class="control-label col-md-4">Barcode</span>
            <input name="barcode" type="number" class="form-control"
                   placeholder="Barcode"
                   %if item:
                   value="{{item.barcode}}"
                   %end
                   required autofocus>
          </label>

          <label for="numCopies" class="form-group control-label" style="display: block">
            <span class="control-label">Copies</span>
            <input name="num_copies" type="number" class="form-control"
                   placeholder="Number of copies to be made available for simultaneous loans"
                   step="any" min="1"
                   %if item:
                   value="{{item.num_copies}}"
                   %end
                   required>
          </label>

          <label for="numCopies" class="form-group control-label" style="display: block">
            <span class="control-label">Loan duration (in hours)</span>
            <input name="duration" type="number" class="form-control"
                   placeholder="Maximum duration of a loan (in hours)"
                   step="any" min="1"
                   %if item:
                   value="{{item.duration}}"
                   %end
                   required>
          </label>

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


      %include('common/footer.tpl')
    </div>
  </body>
</html>
