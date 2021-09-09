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
          Note that DIBS does not change the item status in the 
          library catalog. The catalog record should be updated manually
          to reflect the fact that some copies have been pulled from
          circulation and made available via DIBS.
        </p>

        <form action="{{base_url}}/update/{{action}}" method="POST">
          <div class="row">
            <div class="col-6"><!--left side -->
              <div class="form-group row col-12">
                <label for="barcode" class="col-form-label">Barcode:</label>
                <input name="barcode" type="number" class="form-control"
                       placeholder="Barcode number"
                       %if item:
                       value="{{item.barcode}}"
                       %end
                       required autofocus>
              </div>

              <div class="form-group row col-12">
                <label for="duration" class="col-form-label">Loan duration (in hours):</label>
                <input name="duration" type="number" class="form-control"
                       placeholder="Number of hours"
                       step="any" min="1"
                       %if item:
                       value="{{item.duration}}"
                       %end
                       required>
              </div>
            </div>

            <div class="col-6"><!--right side -->
              <div class="form-group row col-12">
                <label for="num_copies" class="col-form-label">Number of copies to make available:</label>
                <input name="num_copies" type="number" class="form-control"
                       placeholder="Number of copies"
                       step="any" min="1"
                       %if item:
                       value="{{item.num_copies}}"
                       %end
                       required>

              </div>
            </div>
          </div>

          <div class="form-group row col-12">
            <label for="notes" class="form-group control-label">
              Notes (optional; internal use only &ndash; not shown to patrons):
            </label>
            <textarea name="notes" id="notes" class="form-control"
                      rows="4" placeholder="Note text">\\
               %if item:
{{item.notes}}\\
               %end
</textarea>
          </div>

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
