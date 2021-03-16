<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    %include('common/standard-inclusions.tpl')

    <title>List of items currently in Caltech DIBS</title>

    <link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.css">
    <script src="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.6/clipboard.min.js"></script>
  </head>

  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container-fluid main-container">
        <h2 class="mx-auto text-center pb-2 mt-4">
          Items in DIBS
        </h2>
        <div class="d-grid gap-3">

          <div class="mb-3 table-responsive">
            <table class="table table-borderless"
                   data-toggle="table" data-pagination="true" data-escape="false">
              <thead class="thead-light align-bottom align-text-bottom">
                <tr>
                  <th data-sortable="true" data-sorter="linkedNumberSort"
                      data-field="barcode">&nbsp;<br>&nbsp;<br>Barcode</th>

                  <th data-sortable="true" data-sorter="linkedTextSort"
                      data-field="title">&nbsp;<br>&nbsp;<br>Title</th>

                  <th data-sortable="true" data-field="author">&nbsp;<br>&nbsp;<br>Author</th>

                  <th class="text-center" data-sortable="true"
                      data-field="available">Available<br>to<br>loan?</th>

                  <th class="text-center" data-sortable="true" data-field="time"
                      data-sorter="numberSort">Loan<br>time<br>(hrs)</th>

                  <th class="text-center" data-sortable="true" data-field="copies"
                       data-sorter="numberSort">Copies<br>for<br>loans</th>

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

                  <td>
                    {{item.author}}
                  </td>

                  <td class="text-center">
                    <form action="{{base_url}}/ready" method="POST">
                      <input type="hidden" name="barcode" value="{{item.barcode}}">
                      <input type="checkbox" class="checkbox"
                             onChange="this.form.submit()"
                             {{'checked="checked"' if item.ready else ''}}/>
                    </form>
                  </td>

                  <td class="text-center">
                    {{item.duration}}
                  </td>

                  <td class="text-center">
                    {{item.num_copies}}
                  </td>

                  <td>
                    <button id="copyBtn" type="button" class="btn btn-secondary btn-sm"
                            onclick="copyToClipboard(this, '{{base_url}}/item/{{item.barcode}}');">
                      Copy&nbsp;link</button>
                  </td>

                  <td>
                    <form action="{{base_url}}/edit/{{item.barcode}}" method="GET">
                      <input type="hidden" name="barcode" value="{{item.barcode}}"/>
                      <input type="submit" name="edit" value="Edit&nbsp;entry"
                             class="btn btn-info btn-sm"/>
                    </form>
                  </td>
                </tr>
                %end
              </tbody>
            </table>
          </div>

          <div class="mx-auto w-50 text-center">
            <a href="{{base_url}}/add"
               class="btn btn-primary m-0 mr-2 my-2 no-underline">
              Add new item
            </a>
            <a href="{{base_url}}/manage"
               class="btn btn-danger m-0 mr-2 my-2 no-underline">
              Manage item list
            </a>
          </div>

        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
