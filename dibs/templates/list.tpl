<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    %include('common/standard-inclusions.tpl')

    <title>List of items currently in Caltech DIBS</title>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.6/clipboard.min.js"></script>
  </head>

  <script>
   // This next function is based in part on the posting by user Alvaro Montoro
   // to Stack Overflow 2015-06-18, https://stackoverflow.com/a/30905277/743730
   function copyToClipboard(button, text) {
     var aux = document.createElement("input");
     aux.setAttribute("value", text);
     document.body.appendChild(aux);
     aux.select();
     document.execCommand("copy");
     document.body.removeChild(aux);

     // The following code is based in part on a 2016-09-21 posting to Stack
     // Overflow by user Nina Scholz: https://stackoverflow.com/a/39610851/743730
     var last = button.innerHTML;
     button.innerHTML = 'Copied!';
     clicked = true;
     setTimeout(function () {
       button.innerHTML = last;
       clicked = false;
     }.bind(button), 800);
   }
  </script>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <h2 class="mx-auto text-center w-75 pb-2 mt-4">
        There are {{len(items)}} items in the system
      </h2>
      <div class="d-grid gap-3">

        <div class="mb-3">
          <table class="table">
            <thead class="thead-light">
              <tr>
                <th>Barcode</th>
                <th>Title</th>
                <th>Author</th>
                <th class="text-center">Ready<br>to<br>loan?</th>
                <th class="text-center">Loan<br>duration<br>(hrs)</th>
                <th class="text-center">Copies<br>for<br>loans</th>
                <th class="text-center">Copies<br>in<br>use</th>
                <th></th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
            %for item in items:
              <tr scope="row">
                <td>{{item.barcode}}</td>
                <td>
                  %if item.tind_id != '':
                  <a target="_blank" href="https://caltech.tind.io/record/{{item.tind_id}}">{{item.title}}</a>
                  %else:
                  {{item.title}}
                  %end
                <td>{{item.author}}</td>
                <td class="text-center">
                  <form action="{{base_url}}/ready" method="POST">
                    <input type="hidden" name="barcode" value="{{item.barcode}}">
                    <input type="hidden" name="ready" value="{{item.ready}}">
                    <input type="checkbox" class="checkbox"
                           onChange="this.form.submit()"
                           {{'checked="checked"' if item.ready else ''}}/>
                  </form>
                </td>
                <td class="text-center">{{item.duration}}</td>
                <td class="text-center">{{item.num_copies}}</td>
                <td class="text-center">{{len([x for x in loans if x.item.barcode == item.barcode])}}</td>

                <td><button id="copyBtn" type="button" class="btn btn-secondary btn-sm"
                            onclick="copyToClipboard(this, '{{base_url}}/item/{{item.barcode}}');">
                  Copy&nbsp;link</button>
                </td>

                <td>
                  <form action="{{base_url}}/edit/{{item.barcode}}" method="GET">
                    <input type="hidden" name="barcode" value="{{item.barcode}}"/>
                    <input type="submit" name="edit" value="Edit"
                            class="btn btn-info btn-sm"/>
                  </form>
                </td>

                <td>
                  <form action="{{base_url}}/remove" method="POST"
                        onSubmit="return confirm('Remove entry for {{item.barcode}} (&#8220;{{item.title}}&#8221; by {{item.author}})? This will not delete the files from storage, but will remove the entry from the loan database.');">
                    <input type="hidden" name="barcode" value="{{item.barcode}}"/>
                    <input type="submit" name="remove" value="Remove"
                           class="btn btn-danger btn-sm"/>
                  </form>
                </td>
              </tr>
            %end
            </tbody>
          </table>
        </div>

        <div class="py-3 mx-auto" style="width: 150px">
          <a href="{{base_url}}/add" class="btn btn-primary m-0 no-underline">Add a new item</a>
        </div>

      </div>

      %include('common/footer.html')
    </div>

  </body>
</html>
