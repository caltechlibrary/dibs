<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Add or edit a Caltech DIBS entry</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container  mx-auto mt-4">
        <h2 class="mx-auto text-center pb-2">
          %if item:
          Edit item with barcode {{item.barcode}}
          %else:
          Add new item to DIBS
          %end
        </h2>
        <p class="col-10 mx-auto font-italic">
          Please note that DIBS does not change the item status
          in TIND. The TIND record should be updated manually to reflect
          the fact that some copies have been pulled from circulation and
          made available via DIBS.
        </p>

        <form class="form-horizontal" action="{{base_url}}/update/{{action}}" method="POST">

          <label for="barcode" class="form-group control-label" style="display: block">
            <span class="control-label">Barcode</span>
            <input name="barcode" type="number" class="form-control"
                   placeholder="Barcode"
                   %if item:
                   value="{{item.barcode}}"
                   %end
                   required autofocus>
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

          <label for="numCopies" class="form-group control-label" style="display: block">
            <span class="control-label">Number of copies</span>
            <input name="num_copies" type="number" class="form-control"
                   placeholder="Number of copies to be made available for simultaneous loans"
                   step="any" min="1"
                   %if item:
                   value="{{item.num_copies}}"
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
