<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="refresh" content="10">
    %include('common/standard-inclusions.tpl')

    <title>DIBS status page</title>

    <link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.css">
    <script src="https://unpkg.com/bootstrap-table@1.18.2/dist/bootstrap-table.min.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.6.0/css/all.css">
  </head>

  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container-fluid main-container">
        <h2 class="mx-auto text-center pb-2 mt-4">
          Loan statistics
        </h2>
        <p class="mx-auto text-center font-italic">
          Click on the column titles to sort the table by that column.
        </p>
        </p>
        <div class="d-grid gap-3">
          <div class="mb-3 table-responsive">
            <table class="table table-borderless"
                   data-page-size="50"
                   data-toggle="table" data-pagination="true" data-escape="false">
              <thead class="thead-light align-bottom align-text-bottom">
                <tr>
                  <th data-sortable="true" data-sorter="linkedNumberSort"
                      data-field="barcode">&nbsp;<br>&nbsp;<br>Barcode</th>

                  <th data-sortable="true" data-sorter="linkedTextSort"
                      data-field="title">&nbsp;<br>&nbsp;<br>Title</th>

                  <th data-sortable="true"
                      data-field="author">&nbsp;<br>&nbsp;<br>Author</th>

                  <th class="text-center" data-sortable="true"
                      data-field="available">Current<br>active<br>loans</th>

                  <th class="text-center" data-sortable="true" data-field="time"
                      data-sorter="numberSort">Total<br>loans<br>to&nbsp;date</th>

                  <th class="text-center" data-sortable="true" data-field="copies"
                       data-sorter="numberSort">Average<br>loan<br>duration</th>

                  <th class="text-center">
                    Content<br>retrievals<br>
                    <span style="letter-spacing: -1px; font-size: 0.9rem">15/30/45/60</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                %for (item, current_loans, total_loans, avg_duration, retrievals) in usage_data:
                <tr scope="row" 
                    %if current_loans > 0:
                    class="font-weight-bold"
                    %end
                  >
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
                    {{item.author[:50]+"..." if len(item.author) > 50 else item.author}}
                  </td>

                  <td>
                    {{current_loans}}
                  </td>

                  <td>
                    {{total_loans}}
                  </td>

                  <td>
                    {{avg_duration}}
                  </td>

                  <td class="text-center text-monospace m-0 p-0" style="letter-spacing: -4px">
                    %include('common/bar.tpl', value = retrievals[0])
                    %include('common/bar.tpl', value = retrievals[1])
                    %include('common/bar.tpl', value = retrievals[2])
                    %include('common/bar.tpl', value = retrievals[3])
                  </td>

                </tr>                
                %end
              </tbody>
            </table>
          </div>

          <div class="mx-auto w-50 text-center">
            <a href="{{base_url}}/list"
               class="btn btn-primary m-0 mr-2 my-2 no-underline">
              Return to list page
            </a>
          </div>

        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
