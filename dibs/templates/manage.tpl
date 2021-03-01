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
          Manage DIBS item list
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

                  <th data-sortable="true"
                      data-field="author">&nbsp;<br>&nbsp;<br>Author</th>

                  <th data-sortable="true" data-sorter="numberSort"
                      data-field="year">&nbsp;<br>&nbsp;<br>Year</th>

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

                  <td>
                    {{item.year}}
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

        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
