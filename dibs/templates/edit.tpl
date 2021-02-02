<!DOCTYPE html>
<html lang="en">
  <!--
  Thank you for using
     ______          __  __                 __         ____    ____  ____   _____
    / ____/ ____ _  / / / /_  ___   _____  / /_       / __ \  /  _/ / __ ) / ___/
   / /     / __ `/ / / / __/ / _ \ / ___/ / __ \     / / / /  / /  / __  | \__ \ 
  / /___  / /_/ / / / / /_  /  __// /__  / / / /    / /_/ / _/ /  / /_/ /  __/ / 
  \____/  \__,_/ /_/  \__/  \___/ \___/ /_/ /_/    /_____/ /___/ /_____/ /____/  
  
  Please help us to improve this system by reporting problems using the
  GitHub issue system at https://github.com/caltechlibrary/dibs/issues
  or over email at helpdesk@library.caltech.edu
  -->                           
  <head>
    <title>Add or edit a Caltech DIBS entry</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <style>
     ::-webkit-input-placeholder                   { color: #bbb; }
     html .form-control::placeholder               { color: #bbb; }
     html .form-control::-webkit-input-placeholder { color: #bbb; }
     html .form-control:-moz-placeholder           { color: #bbb; }
     html .form-control::-moz-placeholder          { color: #bbb; }
     html .form-control:-ms-input-placeholder      { color: #bbb; }
    </style>
  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto text-center w-100 my-3">
        %if action == "add":
        Add a new item to DIBS
        %else:
        Edit {{item.barcode}}
        %end
      </h2>
      <div class="d-grid">
        <p class="w-75 text-center mx-auto">
          This will add a new item to the DIBS database. Note that it will
          not be made available to patrons for digital loans until the
          "ready" checkbox is checked in the list page.
        </p>

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
                <input class="btn btn-default mx-2" style="width: 100px"
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
  </body>

</html>
