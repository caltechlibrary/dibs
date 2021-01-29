<!DOCTYPE html>
<html lang="en">

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

    <script>
     // The following code is based on a 2019-07-17 posting by user Jeff Tian
     // to Stack Overflow at https://stackoverflow.com/a/57069660/743730
     'use strict';
     (() => {
       const modified_inputs = new Set();
       const defaultValue = 'defaultValue';

       // store default values
       addEventListener('beforeinput', evt => {
         const target = evt.target;
         if (!(defaultValue in target.dataset)) {
           target.dataset[defaultValue] = ('' + (target.value || target.textContent)).trim();
         }
       });

       // detect input modifications
       addEventListener('input', evt => {
         const target = evt.target;
         let original = target.dataset[defaultValue];
         let current  = ('' + (target.value || target.textContent)).trim();

         if (original !== current) {
           if (!modified_inputs.has(target)) {
             modified_inputs.add(target);
           }
         } else if (modified_inputs.has(target)) {
           modified_inputs.delete(target);
         }
       });

       addEventListener('saved', evt => { modified_inputs.clear() }, false
       );

       addEventListener('beforeunload', evt => {
         if (modified_inputs.size) {
           const unsaved_changes_warning = 'Changes you made may not be saved.';
           evt.returnValue = unsaved_changes_warning;
           return unsaved_changes_warning;
         }
       });

     })();
    </script>
    
  </head>
  
  <body>
    <div class="container-fluid">
      <h2 class="mx-auto text-center w-100">
        %if action == "add":
        Add a new item to DIBS
        %else:
        Edit {{item.barcode}}
        %end
      </h2>
      <div class="d-grid">

        <div class="jumbotron">
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
                   placeholder="# copies to be made available"
                   %if item:
                   value="{{item.num_copies}}"
                   %end
                   required>

            <label for="duration" class="sr-only">Loan duration (in hours)</label>
            <input name="duration" type="number" class="form-control"
                   placeholder="hours per loan"
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
