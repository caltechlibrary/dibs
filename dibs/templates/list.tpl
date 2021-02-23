<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    %include('common/standard-inclusions.tpl')

    <title>List of items currently in Caltech DIBS</title>
  </head>

  <link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.css">

  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"
          integrity="sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg=="
          crossorigin="anonymous"></script>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
          integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
          crossorigin="anonymous"></script>

  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
          integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
          crossorigin="anonymous"></script>

  <script src="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.js"></script>

  <script src="https://unpkg.com/bootstrap-table@1.15.5/dist/extensions/natural-sorting/bootstrap-table-natural-sorting.min.js"></script>

  <script>
   // This next function was inspired in part by the posting by user "Undry"
   // to Stack Overflow 2020-07-16, https://stackoverflow.com/a/62928804/743730
   function numberSort(a, b) {
     var aa = +((a + '').replace(/[^\d]/g, ''));
     var bb = +((b + '').replace(/[^\d]/g, ''));
     if (aa < bb) return -1;
     if (aa > bb) return 1;
     return 0;
   }

   function linkedNumberSort(a, b) {
     var aa = +(($(a).text() + '').replace(/[^\d]/g, ''));
     var bb = +(($(b).text() + '').replace(/[^\d]/g, ''));
     if (aa < bb) return -1;
     if (aa > bb) return 1;
     return 0;
   }

   function linkedTextSort(a, b) {
     var a = $(a).text();
     var b = $(b).text();
     if (a < b) return -1;
     if (a > b) return 1;
     return 0;
   }

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
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container-fluid main-container">
        <h2 class="mx-auto text-center w-75 pb-2 mt-4">
          There are {{len(items)}} items in the system
        </h2>
        <div class="d-grid gap-3">

          <div class="mb-3 table-responsive-sm">
            <table class="table" data-toggle="table" data-pagination="true" data-escape="false">
              <thead class="thead-light">
                <tr>
                  <th data-sortable="true" data-sorter="linkedNumberSort"
                      data-field="barcode">Barcode</th>

                  <th data-sortable="true" data-sorter="linkedTextSort"
                      data-field="title">Title</th>

                  <th data-sortable="true" data-field="author">Author</th>

                  <th class="text-center" data-sortable="true"
                      data-field="available">Available<br>to<br>loan?</th>

                  <th class="text-center" data-sortable="true" data-field="time"
                      data-sorter="numberSort">Loan<br>time<br>(hrs)</th>

                  <th class="text-center" data-sortable="true" data-field="copies"
                       data-sorter="numberSort">Copies<br>for<br>loans</th>

                  <th class="text-center" data-sortable="true" data-field="in-use"
                       data-sorter="numberSort">Copies<br>in<br>use</th>

                  <th></th>

                  <th></th>

                  <th></th>
                </tr>
              </thead>
              <tbody>
                %for item in items:
                <tr scope="row">
                  <td>
                    %if item.tind_id != '':
                    <a href="https://caltech.tind.io/record/{{item.tind_id}}">{{item.barcode}}</a>
                    %else:
                    {{item.barcode}}
                    %end
                  </td>

                  <td>
                    <a href="{{base_url}}/item/{{item.barcode}}">{{item.title}}</a>
                  </td>

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
                          onSubmit="return confirm('Remove list entry for {{item.barcode}} '
                                                   + '(&#8220;{{item.title}}&#8221; by '
                                                   + '{{item.author}})? This will not '
                                                   + 'delete the files from storage; '
                                                   + 'it will simply delist the entry '
                                                   + 'from the DIBS database.');">
                      <input type="hidden" name="barcode" value="{{item.barcode}}"/>
                      <input type="submit" name="remove" value="Delist"
                             class="btn btn-danger btn-sm"/>
                    </form>
                  </td>
                </tr>
                %end
              </tbody>
            </table>
          </div>

          <div class="py-3 mx-auto w-25 text-center">
            <a href="{{base_url}}/add" class="btn btn-primary m-0 no-underline">Add a new item</a>
          </div>

        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
